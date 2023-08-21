
template = """Use the following pieces of context to answer the Question at the end. If you don't know the answer, just say that you don't know, don't try to make up an answer.
--------
{context}
--------
Question: {question}

Please the provide the following in json JSON format with following keys answer, source_url and confidence_score."""
DEFAULT_OUTPUT_QnA_MAKER = {"answer": "No answer found", "prompts":[], "confidence": 1.0, "source": "", "source_url": "N/A"}
DEFAULT_OUTPUT_OpenAI = {"answer": "No answer found", "prompts":[], "confidence": 1.0, "source": "OpenAI", "source_url": "N/A"}
DEFAULT_GENERIC_OUTPUT = {"answer": "No answer found", "prompts":[], "confidence": 1.0, "source":"", "source_url": "N/A"}
URLS=["http://fissionlabs.com/about-us",
      "http://fissionlabs.com/how-we-work",
      "http://fissionlabs.com/public-relations-csr",
      "http://fissionlabs.com/careers",
      "http://fissionlabs.com/contact-us",
      "http://fissionlabs.com/services/web-mobile-application-development-services",
      "http://fissionlabs.com/services/data-engineering-services",
      "http://fissionlabs.com/services/cloud-consulting-services",
      "http://fissionlabs.com/services/ai-ml-based-solutions",
      "http://fissionlabs.com/services/quality-assurance-services",
      "http://fissionlabs.com/services/salesforce-consulting-services",
      "http://fissionlabs.com/blog",
      "http://fissionlabs.com/case-studies",
      "https://www.fissionlabs.com/case-study/hospital-management-analytics-platform",
      "http://fissionlabs.com/case-study/ai-based-object-volume-estimator",
      "http://fissionlabs.com/case-study/multi-device-iot-communication-platform",
      "http://fissionlabs.com/case-study/realtime-health-records-monitoring-platform",
      "http://fissionlabs.com/case-study/fully-automated-managed-cloud-services-platform-for-healthcare-industry",
      "http://fissionlabs.com/case-study/advertising-sales-automation-workflow-platform",
      "https://www.fissionlabs.com/case-study/fleet-tracking-portal",
      "https://www.fissionlabs.com/case-study/pathology-radiology-e-learning-platform",
      "https://www.fissionlabs.com/case-study/enterprise-hrms-labour-analysis-platform",
      "http://fissionlabs.com/case-studies/integrated-campaign-management-platform",
      "http://fissionlabs.com/case-studies/workflow-management-platform",
      "http://fissionlabs.com/case-studies/iot-driven-fleet-management-platform",
      "http://fissionlabs.com/case-studies/life-science-and-regulatory-platform",
      "http://fissionlabs.com/case-studies/integrated-telehealth-platform",
      "http://fissionlabs.com/e-book-whitepapers",
      "http://fissionlabs.com/blog-posts/selecting-the-right-software-development-vendor-how-proof-of-concept-trials-can-help",
    ]
