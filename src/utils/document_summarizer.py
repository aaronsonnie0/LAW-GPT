import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DocumentSummarizer:
    """
    Utility for summarizing legal documents and highlighting risky clauses
    """

    def __init__(self):
        """
        Initialize the document summarizer
        """
        # Initialize the LLM
        try:
            self.llm = ChatGoogleGenerativeAI(
                google_api_key=os.getenv("GOOGLE_API_KEY"),
                model="gemini-1.5-pro",
                temperature=0.0
            )
        except Exception as e:
            print(f"Error initializing LLM for document summarization: {e}")
            self.llm = None

        # Initialize the chains
        self.summary_prompt = None
        self.summary_chain = None
        self.risk_prompt = None
        self.risk_chain = None

        if self.llm is not None:
            try:
                # Create a prompt template for document summarization
                summary_template = """
                You are a legal AI specialized in analyzing and summarizing legal documents.

                Provide a comprehensive summary of the following legal document based on the clauses provided.
                Focus on the key points, obligations, rights, and potential risks.

                Clauses:
                {clauses}

                Your summary should include:
                1. Document Type and Purpose
                2. Key Parties
                3. Main Obligations
                4. Important Dates and Deadlines
                5. Financial Terms
                6. Termination Conditions
                7. Potential Risks and Red Flags

                Format your response in markdown with appropriate headings and bullet points.
                """

                self.summary_prompt = PromptTemplate(
                    template=summary_template,
                    input_variables=["clauses"]
                )

                self.summary_chain = LLMChain(
                    llm=self.llm,
                    prompt=self.summary_prompt
                )

                # Create a prompt template for risk highlighting
                risk_template = """
                You are a legal AI specialized in identifying risks in legal documents.

                Analyze the following clause and identify any parts that present legal risks.
                Focus on:
                - High penalties
                - Termination triggers
                - Unclear obligations
                - One-sided terms
                - Potential legal compliance issues

                Clause:
                {clause}

                Output your answer in the following format:
                Risk Level: [High/Medium/Low]
                Highlighted Risks:
                - [First risk identified]
                - [Second risk identified]
                - ...
                Recommendations:
                - [Recommendation 1]
                - [Recommendation 2]
                - ...
                """

                self.risk_prompt = PromptTemplate(
                    template=risk_template,
                    input_variables=["clause"]
                )

                self.risk_chain = LLMChain(
                    llm=self.llm,
                    prompt=self.risk_prompt
                )
            except Exception as e:
                print(f"Error creating chains for document summarization: {e}")
                self.summary_chain = None
                self.risk_chain = None



    def summarize_document(self, clauses):
        """
        Summarize a document based on its clauses

        Args:
            clauses: List of clause dictionaries

        Returns:
            Document summary
        """
        if self.summary_chain is None:
            return self._generate_basic_summary(clauses)

        try:
            # Add a timeout mechanism to prevent getting stuck
            import threading

            result_container = [None]
            error_container = [None]

            # Prepare the clauses text
            clauses_text = ""
            for clause in clauses:
                clauses_text += f"Clause {clause['id']} ({clause.get('type', 'Unknown')}): {clause['text']}\n\n"

            def summarize_with_timeout():
                try:
                    result_container[0] = self.summary_chain.run(clauses=clauses_text)
                except Exception as e:
                    error_container[0] = str(e)

            # Start summarization in a separate thread
            thread = threading.Thread(target=summarize_with_timeout)
            thread.start()

            # Wait for the thread to complete with a timeout
            timeout = 15  # seconds
            thread.join(timeout)

            # Check if summarization completed or timed out
            if thread.is_alive():
                print("Summarization is taking longer than expected. Using basic summary.")
                return self._generate_basic_summary(clauses)
            elif error_container[0]:
                print(f"Error during summarization: {error_container[0]}. Using basic summary.")
                return self._generate_basic_summary(clauses)

            summary = result_container[0]
            return summary
        except Exception as e:
            print(f"Error summarizing document: {e}")
            return self._generate_basic_summary(clauses)

    def _generate_basic_summary(self, clauses):
        """
        Generate a basic summary when LLM is not available

        Args:
            clauses: List of clause dictionaries

        Returns:
            Basic document summary
        """
        # Extract document type based on clause types
        clause_types = {}
        for clause in clauses:
            clause_type = clause.get('type', 'Unknown')
            if clause_type != 'Unknown':
                clause_types[clause_type] = clause_types.get(clause_type, 0) + 1

        # Find the most common clause type
        document_type = "Legal Document"
        if clause_types:
            document_type = max(clause_types.items(), key=lambda x: x[1])[0]
            if document_type == "Financial":
                document_type = "Financial Agreement"
            elif document_type == "IP":
                document_type = "Intellectual Property Agreement"
            elif document_type == "Confidentiality":
                document_type = "Confidentiality Agreement"
            elif document_type == "Termination":
                document_type = "Service Agreement"
            else:
                document_type = f"{document_type} Agreement"

        # Count high-risk clauses
        high_risk_count = sum(1 for clause in clauses if clause.get('risk_score', 0) >= 4)

        # Generate a basic summary
        summary = f"""
# Document Summary

## Document Type and Purpose
This appears to be a **{document_type}** containing {len(clauses)} clauses.

## Key Points
- The document contains clauses related to: {', '.join(clause_types.keys())}
- {high_risk_count} high-risk clauses were identified

## Clause Breakdown
"""

        # Add clause breakdown
        for clause_type, count in clause_types.items():
            summary += f"- {clause_type}: {count} clauses\n"

        summary += """
## Note
This is a basic summary generated without the full AI analysis. For a more detailed analysis, please ensure all dependencies are properly installed.
"""

        return summary

    def highlight_risks(self, clause_text):
        """
        Highlight risks in a clause

        Args:
            clause_text: The text of the clause

        Returns:
            Risk analysis
        """
        if self.risk_chain is None:
            return self._generate_basic_risk_analysis(clause_text)

        try:
            # Add a timeout mechanism to prevent getting stuck
            import threading

            result_container = [None]
            error_container = [None]

            def analyze_with_timeout():
                try:
                    result_container[0] = self.risk_chain.run(clause=clause_text)
                except Exception as e:
                    error_container[0] = str(e)

            # Start risk analysis in a separate thread
            thread = threading.Thread(target=analyze_with_timeout)
            thread.start()

            # Wait for the thread to complete with a timeout
            timeout = 10  # seconds
            thread.join(timeout)

            # Check if analysis completed or timed out
            if thread.is_alive():
                print("Risk analysis is taking longer than expected. Using basic analysis.")
                return self._generate_basic_risk_analysis(clause_text)
            elif error_container[0]:
                print(f"Error during risk analysis: {error_container[0]}. Using basic analysis.")
                return self._generate_basic_risk_analysis(clause_text)

            risk_analysis = result_container[0]
            return risk_analysis
        except Exception as e:
            print(f"Error highlighting risks: {e}")
            return self._generate_basic_risk_analysis(clause_text)

    def _generate_basic_risk_analysis(self, clause_text):
        """
        Generate a basic risk analysis when LLM is not available

        Args:
            clause_text: The text of the clause

        Returns:
            Basic risk analysis
        """
        text_lower = clause_text.lower()

        # Check for high-risk keywords
        high_risk_terms = [
            'terminate', 'termination', 'penalty', 'penalties', 'damages',
            'liability', 'indemnify', 'indemnification', 'unlimited',
            'warrant', 'warranty', 'guarantees', 'breach', 'violation'
        ]

        medium_risk_terms = [
            'confidential', 'disclosure', 'proprietary', 'intellectual property',
            'payment', 'fee', 'compensation', 'tax', 'taxes', 'deadline'
        ]

        # Count risk terms
        high_risk_count = sum(1 for term in high_risk_terms if term in text_lower)
        medium_risk_count = sum(1 for term in medium_risk_terms if term in text_lower)

        # Determine risk level
        if high_risk_count >= 2:
            risk_level = "High"
        elif high_risk_count == 1 or medium_risk_count >= 2:
            risk_level = "Medium"
        else:
            risk_level = "Low"

        # Generate highlighted risks
        highlighted_risks = []

        if 'terminate' in text_lower or 'termination' in text_lower:
            highlighted_risks.append("Contains termination provisions")

        if 'penalty' in text_lower or 'penalties' in text_lower:
            highlighted_risks.append("Contains penalty provisions")

        if 'damages' in text_lower:
            highlighted_risks.append("References damages")

        if 'liability' in text_lower:
            highlighted_risks.append("Contains liability provisions")

        if 'indemnify' in text_lower or 'indemnification' in text_lower:
            highlighted_risks.append("Contains indemnification requirements")

        if 'unlimited' in text_lower:
            highlighted_risks.append("May contain unlimited obligations")

        if 'warrant' in text_lower or 'warranty' in text_lower:
            highlighted_risks.append("Contains warranty provisions")

        if not highlighted_risks:
            highlighted_risks.append("No specific risks identified through basic analysis")

        # Generate recommendations
        recommendations = ["Review with legal counsel"]

        if risk_level == "High":
            recommendations.append("Pay special attention to this clause")

        # Format the analysis
        analysis = f"""Risk Level: {risk_level}
Highlighted Risks:
- {"\n- ".join(highlighted_risks)}

Recommendations:
- {"\n- ".join(recommendations)}

Note: This is a basic risk analysis generated without the full AI analysis.
"""

        return analysis

    def analyze_document_risks(self, clauses):
        """
        Analyze risks in all clauses of a document

        Args:
            clauses: List of clause dictionaries

        Returns:
            Updated list of clauses with risk analysis
        """
        try:
            for clause in clauses:
                clause['risk_analysis'] = self.highlight_risks(clause['text'])

            return clauses
        except Exception as e:
            print(f"Error analyzing document risks: {e}")
            for clause in clauses:
                clause['risk_analysis'] = self._generate_basic_risk_analysis(clause['text'])
            return clauses
