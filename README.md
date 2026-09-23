# IP-SAKTHI Sahayak

## AI-Powered Multilingual Ayurveda IP & Innovation Assistant

IP-SAKTHI Sahayak is a multimodal AI-powered prototype designed to assist users in identifying Ayurvedic plants, herbal components, and Ayurvedic products using either images or text.

The system provides structured information related to plants, components, products, safety, growth, distribution, medicinal-system comparisons, and potential future innovations.

---

## Problem

Information related to Ayurvedic plants, herbal components, traditional uses, safety, cultivation, intellectual property, and innovation is often distributed across multiple sources.

Users may face difficulty in:

* Identifying an unknown herbal plant or component
* Understanding its traditional uses
* Finding its geographical distribution
* Understanding its growth timeline
* Assessing safety and toxicity information
* Exploring potential products that can be developed from a plant/component
* Comparing Ayurveda with other systems of medicine
* Finding relevant Ayurveda-related IP and regulatory information

IP-SAKTHI Sahayak aims to bring these capabilities together into a single AI-assisted platform.

---

# Key Features

## 1. Image-Based Identification

Users can upload an image of:

* Ayurvedic plants
* Herbal components
* Raw materials
* Ayurvedic products

The vision model analyzes the uploaded image and identifies the most likely item.

```text
Image
  ↓
Qwen3-VL Vision Model
  ↓
Identification
  ↓
Knowledge Database
  ↓
Detailed Result
```

---

## 2. Text-Based Search

Users can enter or select the name of a:

* Plant
* Herbal component
* Ayurvedic product

The system retrieves the corresponding information from the knowledge base.

---

## 3. Plant Information

The prototype can provide:

* Common name
* Scientific name
* Botanical family
* Plant type
* Rarity/status
* Distribution
* Growth time
* Growth stages
* Traditional uses

---

## 4. Component & Product Information

The system supports information retrieval for:

* Herbal components
* Ayurvedic raw materials
* Ayurvedic products

The same analysis interface can be used for both individual components and complete products.

---

## 5. Safety & Toxicity Information

The prototype provides structured safety information including:

* Safety level
* Potential adverse effects
* Interaction considerations
* Toxicity information

---

## 6. Growth Timeline

Growth information is displayed dynamically according to the selected plant.

Different plants can have different:

* Germination periods
* Vegetative stages
* Maturity periods
* Harvest periods
* Overall growth durations

---

## 7. Medicine-System Comparison

The prototype provides an informational comparison between Ayurveda and other systems of medicine, including:

* Ayurveda
* Allopathy
* Homeopathy
* Other available systems

The comparison can include recovery-related information where supported by the available data.

> This feature is intended for informational and educational purposes and should not be interpreted as medical advice.

---

## 8. Geographical Distribution

The system provides information about locations where an identified plant or species can be found.

Future versions can integrate GIS-based visualization for geographical exploration.

---

## 9. Future Innovation Suggestions

For an identified plant or component, the system can suggest potential innovation concepts such as:

* Herbal formulations
* Herbal wellness products
* Herbal cosmetics
* Nutraceutical concepts
* Plant-based products
* Research opportunities

These suggestions are intended as innovation ideas and require scientific, safety, regulatory, and expert validation before practical use.

---

## 10. Multilingual Support

The project is designed to support multilingual interaction for improving accessibility to Ayurveda-related information.

Future versions can expand support for Indian languages using language technologies such as Bhashini.

---

# Technology Stack

* Python
* FastAPI
* React
* Vite
* Ollama
* Qwen3-VL
* MySQL
* REST API
* Docker
* GIS
* Bhashini

---

# Architecture

```text
                         USER
                           │
              ┌────────────┴────────────┐
              │                         │
        IMAGE INPUT                TEXT INPUT
              │                         │
              ▼                         ▼
       Qwen3-VL Vision            Search / Query
              │                         │
              └────────────┬────────────┘
                           │
                           ▼
                    FASTAPI BACKEND
                           │
              ┌────────────┼────────────┐
              │            │            │
              ▼            ▼            ▼
           MySQL      Knowledge     AI Processing
                      Database           │
                                        ▼
                                   Qwen3-VL
                           │
                           ▼
                  Structured Information
                           │
                           ▼
                    REACT FRONTEND
                           │
          ┌────────────────┼────────────────┐
          │                │                │
          ▼                ▼                ▼
      Plant Info       Safety Data      Innovation
          │                │                │
          └────────────────┼────────────────┘
                           │
                           ▼
                      User Dashboard
```

---

# Project Structure

```text
ip-sakthi-sahayak/
│
├── frontend/
│   ├── src/
│   ├── public/
│   ├── package.json
│   └── vite.config.js
│
├── backend/
│   ├── main.py
│   └── requirements.txt
│
├── .gitignore
└── README.md
```

---

# Future Developments

The current project is a prototype. The following capabilities can be developed in future versions.

## 1. Advanced Plant & Product Recognition

Improve image recognition using larger and more specialized vision models capable of identifying:

* More Ayurvedic plant species
* Different plant parts
* Dried herbs
* Seeds
* Roots
* Powders
* Herbal extracts
* Ayurvedic products
* Product packaging

---

## 2. Ayurveda Knowledge Graph

Develop a dedicated Ayurveda knowledge graph connecting:

```text
Plant
  │
  ├── Components
  ├── Traditional Uses
  ├── Diseases/Conditions
  ├── Formulations
  ├── Products
  ├── Geographical Regions
  ├── Cultivation
  └── Research/IP
```

Neo4j or another graph database could be incorporated for relationship-based knowledge discovery.

---

## 3. Intellectual Property Search

Expand the system into an Ayurveda-focused IP discovery platform.

Future capabilities could include:

* Patent search
* Prior-art discovery
* Similar invention identification
* Patent classification
* Traditional Knowledge references
* Patent landscape analysis
* Innovation novelty exploration

---

## 4. Regulatory Guidance

Future versions can provide structured guidance related to:

* Product categories
* Regulatory pathways
* Documentation requirements
* Compliance considerations
* Labeling requirements
* Intellectual property considerations

The system can provide source-linked information to help users verify regulatory requirements.

---

## 5. Source-Cited AI Responses

Introduce a stronger Retrieval-Augmented Generation (RAG) pipeline where responses are generated from verified knowledge sources.

Future responses can provide:

```text
Answer
  ↓
Supporting Evidence
  ↓
Source
  ↓
Document / Reference
```

This can improve transparency and reduce unsupported AI-generated information.

---

## 6. GIS-Based Herbal Plant Mapping

Integrate GIS capabilities to create interactive maps showing:

* Species distribution
* Native regions
* Cultivation regions
* Availability
* Environmental conditions
* Potential cultivation zones

---

## 7. Cultivation Assistant

Future versions can provide cultivation-oriented information such as:

* Soil requirements
* Water requirements
* Temperature range
* Sunlight requirements
* Planting season
* Growth stages
* Harvest period
* Sustainable cultivation practices

---

## 8. AI-Based Innovation Generator

The innovation engine can be expanded to explore combinations such as:

```text
Plant / Component
       +
Target Application
       +
Existing Research
       +
Market Need
       ↓
Potential Innovation Concepts
```

The system could generate structured research and product-development ideas while clearly separating AI-generated suggestions from validated scientific evidence.

---

## 9. Formulation Exploration

Future versions could help researchers explore existing Ayurvedic formulations and relationships between:

* Ingredients
* Plant parts
* Preparation methods
* Traditional formulations
* Existing products

Any formulation generated by AI would require expert validation before practical use.

---

## 10. Multilingual Voice Assistant

Add voice-based interaction supporting Indian languages.

Possible workflow:

```text
User Speech
    ↓
Speech Recognition
    ↓
AI Processing
    ↓
Knowledge Retrieval
    ↓
Response Generation
    ↓
Text / Voice Response
```

---

## 11. Mobile Application

Develop dedicated Android/iOS applications allowing users to:

* Photograph a plant
* Identify the plant
* View its information
* Explore geographical distribution
* Save identified plants
* Access multilingual information

---

## 12. Expert Verification System

Introduce an expert-review layer where qualified Ayurveda professionals, botanists, researchers, or domain experts can:

* Verify identifications
* Review information
* Correct knowledge entries
* Validate innovation suggestions
* Provide expert annotations

This can create a human-in-the-loop knowledge system.

---

## 13. Community Knowledge Contribution

Future versions could allow verified users and researchers to contribute:

* Plant observations
* Images
* Traditional knowledge references
* Research papers
* Cultivation information
* Regional information

Submissions can go through moderation and expert verification.

---

## 14. Cloud Deployment

The prototype currently supports local AI processing.

Future deployment can move the system to a cloud architecture:

```text
User
 ↓
React Web App
 ↓
API Gateway
 ↓
FastAPI Backend
 ├── MySQL
 ├── Vector Database
 ├── Knowledge Graph
 └── AI / Vision Model
```

Docker and cloud infrastructure can be used for scalable deployment.

---

## 15. Personalised Research Assistant

A future version could provide researchers with a workspace for:

* Saving plants/components
* Comparing species
* Tracking research
* Saving references
* Exploring related patents
* Generating research summaries
* Creating innovation reports

---

# Future Vision

The long-term vision of IP-SAKTHI Sahayak is to evolve from an identification and information prototype into an integrated **AI-powered Ayurveda knowledge, intellectual-property, research, innovation, and regulatory assistance platform**.

```text
Identify
   ↓
Understand
   ↓
Research
   ↓
Compare
   ↓
Discover IP
   ↓
Explore Innovation
   ↓
Validate
   ↓
Develop
```

---

# Local Development

## Backend

```bash
cd backend
source venv/bin/activate
uvicorn main:app --reload
```

## Frontend

Open another Terminal window:

```bash
cd ~/ip-sakthi-sahayak/frontend
npm run dev
```

---

# AI Model

The prototype uses:

```text
Ollama
    ↓
Qwen3-VL:2B
```

The locally running vision model enables image understanding without requiring a cloud AI API key.

---

