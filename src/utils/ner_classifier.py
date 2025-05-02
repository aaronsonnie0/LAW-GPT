# Try to import spacy
try:
    import spacy
    SPACY_AVAILABLE = True
except ImportError:
    SPACY_AVAILABLE = False
    print("Warning: spaCy not available. NER functionality will be limited.")

import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class NERClassifier:
    """
    Named Entity Recognition and Clause Classification
    """

    def __init__(self):
        """
        Initialize the NER and Classifier
        """
        # Check if spaCy is available
        if not SPACY_AVAILABLE:
            print("NER functionality is disabled because spaCy is not available.")
            print("Please install spaCy with: py -m pip install spacy")
            self.nlp = None
        else:
            # Load spaCy model
            try:
                self.nlp = spacy.load("en_core_web_trf")
            except OSError:
                # If the model is not installed, download it
                import subprocess
                try:
                    subprocess.run(["py", "-m", "spacy", "download", "en_core_web_trf"])
                    self.nlp = spacy.load("en_core_web_trf")
                except:
                    print("Warning: Could not load spaCy model. NER functionality will be limited.")
                    # Use a simple fallback for entities
                    self.nlp = None

        # Initialize the LLM for classification
        try:
            self.llm = ChatGoogleGenerativeAI(
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                model="gemini-1.5-pro",
                temperature=0.0
            )
        except Exception as e:
            print(f"Error initializing LLM for classification: {e}")
            self.llm = None

        # Initialize the classification chain
        self.classification_prompt = None
        self.classification_chain = None

        if self.llm is not None:
            # Create a prompt template for clause classification
            classification_template = """
            You are a legal AI specialized in analyzing legal documents.

            Analyze the following clause and classify it as one of the following types:
            - IP (Intellectual Property)
            - Tax
            - Financial
            - Termination
            - Liability
            - Confidentiality
            - Indemnification
            - Governing Law
            - Other

            Also, provide a risk score from 1-5 (where 5 is highest risk) and explain why.

            Clause:
            {clause}

            Output your answer in the following format:
            Type: [clause type]
            Risk Score: [1-5]
            Explanation: [brief explanation of the classification and risk assessment]
            """

            self.classification_prompt = PromptTemplate(
                template=classification_template,
                input_variables=["clause"]
            )

            try:
                self.classification_chain = LLMChain(
                    llm=self.llm,
                    prompt=self.classification_prompt
                )
            except Exception as e:
                print(f"Error creating classification chain: {e}")
                self.classification_chain = None



    def extract_entities(self, text):
        """
        Extract named entities from text

        Args:
            text: The text to extract entities from

        Returns:
            Dictionary of entities by type
        """
        if self.nlp is None:
            # Fallback if spaCy is not available
            # Use a simple regex-based approach to extract some common entities
            import re

            entities = {}

            # Extract dates (simple pattern)
            date_pattern = r'\b\d{1,2}[/-]\d{1,2}[/-]\d{2,4}\b|\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]* \d{1,2},? \d{4}\b'
            dates = re.findall(date_pattern, text)
            if dates:
                entities["DATE"] = dates

            # Extract monetary values
            money_pattern = r'\$\s*\d+(?:,\d{3})*(?:\.\d{2})?|\d+(?:,\d{3})*(?:\.\d{2})?\s*(?:USD|dollars|EUR|GBP)'
            money = re.findall(money_pattern, text)
            if money:
                entities["MONEY"] = money

            # Extract percentages
            percentage_pattern = r'\d+(?:\.\d+)?\s*%'
            percentages = re.findall(percentage_pattern, text)
            if percentages:
                entities["PERCENTAGE"] = percentages

            # If no entities were found
            if not entities:
                entities["FALLBACK"] = ["NER model not available, using simple pattern matching"]

            return entities

        try:
            doc = self.nlp(text)

            entities = {}
            for ent in doc.ents:
                if ent.label_ not in entities:
                    entities[ent.label_] = []
                entities[ent.label_].append(ent.text)

            return entities
        except Exception as e:
            print(f"Error extracting entities: {e}")
            return {"ERROR": [str(e)]}

    def classify_clause(self, clause_text):
        """
        Classify a clause using the LLM

        Args:
            clause_text: The text of the clause

        Returns:
            Dictionary with classification results
        """
        if self.llm is None or self.classification_chain is None:
            print("LLM for classification is not available")
            # Use a simple rule-based classifier as fallback
            return self._rule_based_classification(clause_text)

        try:
            # Add a timeout mechanism to prevent getting stuck
            import threading
            import time

            result_container = [None]
            error_container = [None]

            def classify_with_timeout():
                try:
                    result_container[0] = self.classification_chain.run(clause=clause_text)
                except Exception as e:
                    error_container[0] = str(e)

            # Start classification in a separate thread
            thread = threading.Thread(target=classify_with_timeout)
            thread.start()

            # Wait for the thread to complete with a timeout
            timeout = 10  # seconds
            thread.join(timeout)

            # Check if classification completed or timed out
            if thread.is_alive():
                print("Classification is taking longer than expected. Using rule-based classification.")
                return self._rule_based_classification(clause_text)
            elif error_container[0]:
                print(f"Error during classification: {error_container[0]}. Using rule-based classification.")
                return self._rule_based_classification(clause_text)

            result = result_container[0]

            # Parse the result
            lines = result.strip().split('\n')
            classification = {}

            for line in lines:
                if line.startswith('Type:'):
                    classification['type'] = line.replace('Type:', '').strip()
                elif line.startswith('Risk Score:'):
                    try:
                        classification['risk_score'] = int(line.replace('Risk Score:', '').strip())
                    except ValueError:
                        classification['risk_score'] = 0
                elif line.startswith('Explanation:'):
                    classification['explanation'] = line.replace('Explanation:', '').strip()

            # If we couldn't parse the result properly, use rule-based classification
            if 'type' not in classification or 'risk_score' not in classification:
                return self._rule_based_classification(clause_text)

            return classification
        except Exception as e:
            print(f"Error classifying clause: {e}")
            return self._rule_based_classification(clause_text)

    def _rule_based_classification(self, text):
        """
        Simple rule-based classification when LLM is not available

        Args:
            text: The text to classify

        Returns:
            Dictionary with classification results
        """
        text_lower = text.lower()

        # Simple rule-based classification
        if any(term in text_lower for term in ['confidential', 'disclose', 'disclosure', 'secret']):
            clause_type = "Confidentiality"
            risk_score = 3
            explanation = "Contains confidentiality provisions."
        elif any(term in text_lower for term in ['intellectual property', 'copyright', 'patent', 'trademark']):
            clause_type = "IP"
            risk_score = 3
            explanation = "Contains intellectual property provisions."
        elif any(term in text_lower for term in ['terminate', 'termination', 'cancel']):
            clause_type = "Termination"
            risk_score = 4
            explanation = "Contains termination provisions."
        elif any(term in text_lower for term in ['payment', 'fee', 'compensation', 'dollar', '$']):
            clause_type = "Financial"
            risk_score = 3
            explanation = "Contains financial provisions."
        elif any(term in text_lower for term in ['tax', 'taxation']):
            clause_type = "Tax"
            risk_score = 3
            explanation = "Contains tax provisions."
        elif any(term in text_lower for term in ['indemnify', 'indemnification', 'hold harmless']):
            clause_type = "Indemnification"
            risk_score = 4
            explanation = "Contains indemnification provisions."
        elif any(term in text_lower for term in ['govern', 'jurisdiction', 'law']):
            clause_type = "Governing Law"
            risk_score = 2
            explanation = "Contains governing law provisions."
        elif any(term in text_lower for term in ['liable', 'liability', 'damage']):
            clause_type = "Liability"
            risk_score = 4
            explanation = "Contains liability provisions."
        else:
            clause_type = "Other"
            risk_score = 2
            explanation = "General clause without specific classification."

        return {
            "type": clause_type,
            "risk_score": risk_score,
            "explanation": explanation
        }

    def process_clauses(self, clauses):
        """
        Process a list of clauses with NER and classification

        Args:
            clauses: List of clause dictionaries

        Returns:
            Updated list of clauses with entities and classification
        """
        for clause in clauses:
            # Extract entities
            clause['entities'] = self.extract_entities(clause['text'])

            # Classify the clause
            classification = self.classify_clause(clause['text'])
            clause.update(classification)

        return clauses
