COMPREHENSIVE_SKILLS = {
    "languages": [
        "python", "java", "javascript", "typescript", "c++", "c#", "go", "rust",
        "kotlin", "swift", "php", "ruby", "scala", "r", "matlab", "bash", "shell",
        "perl", "dart", "elixir", "groovy", "objective-c", "assembly", "cobol",
        "fortran", "haskell", "erlang", "clojure", "f#", "julia", "lua", "vba"
    ],
    "frontend": [
        "react", "angular", "vue", "nextjs", "nuxtjs", "svelte", "jquery",
        "html", "html5", "css", "css3", "sass", "scss", "less", "tailwind",
        "bootstrap", "material ui", "chakra ui", "webpack", "vite", "babel",
        "redux", "mobx", "zustand", "graphql", "apollo", "gatsby", "remix",
        "storybook", "jest", "cypress", "playwright", "figma", "webflow"
    ],
    "backend": [
        "nodejs", "express", "fastapi", "django", "flask", "spring", "springboot",
        "laravel", "rails", "nestjs", "asp.net", "gin", "fiber", "echo",
        "fastify", "hapi", "koa", "strapi", "directus", "hasura",
        "rest api", "graphql api", "grpc", "websocket", "microservices",
        "event driven", "message queue", "rabbitmq", "kafka", "celery"
    ],
    "database": [
        "postgresql", "mysql", "mongodb", "redis", "sqlite", "oracle",
        "cassandra", "elasticsearch", "dynamodb", "firebase", "supabase",
        "neo4j", "mariadb", "cockroachdb", "planetscale", "fauna",
        "influxdb", "timescaledb", "clickhouse", "snowflake", "bigquery",
        "sql", "nosql", "orm", "sqlalchemy", "prisma", "mongoose", "sequelize"
    ],
    "cloud_devops": [
        "aws", "azure", "gcp", "docker", "kubernetes", "terraform", "ansible",
        "jenkins", "github actions", "gitlab ci", "circleci", "travis ci",
        "nginx", "apache", "linux", "ubuntu", "centos", "ci/cd", "helm",
        "prometheus", "grafana", "datadog", "splunk", "elk stack",
        "cloudformation", "pulumi", "vagrant", "packer", "consul", "vault",
        "istio", "linkerd", "envoy", "argocd", "flux", "tekton",
        "s3", "ec2", "lambda", "rds", "cloudfront", "route53", "vpc",
        "azure devops", "gke", "eks", "aks", "cloud run", "cloud functions"
    ],
    "ai_ml": [
        "machine learning", "deep learning", "tensorflow", "pytorch", "keras",
        "scikit-learn", "nlp", "computer vision", "opencv", "pandas", "numpy",
        "matplotlib", "seaborn", "plotly", "jupyter", "huggingface",
        "openai", "langchain", "llamaindex", "transformers", "bert", "gpt",
        "xgboost", "lightgbm", "catboost", "random forest", "svm",
        "neural networks", "cnn", "rnn", "lstm", "attention mechanism",
        "reinforcement learning", "generative ai", "diffusion models",
        "mlflow", "weights and biases", "kubeflow", "airflow", "dbt",
        "feature engineering", "model deployment", "model monitoring",
        "a/b testing", "statistical analysis", "data science", "data analysis",
        "data pipeline", "etl", "spark", "hadoop", "hive", "presto"
    ],
    "mobile": [
        "android", "ios", "react native", "flutter", "xamarin", "ionic",
        "swift", "kotlin", "objective-c", "java android", "expo",
        "mobile ui", "push notifications", "app store", "google play",
        "firebase", "realm", "core data", "room database"
    ],
    "testing": [
        "unit testing", "integration testing", "end to end testing",
        "jest", "pytest", "junit", "mocha", "chai", "jasmine",
        "selenium", "cypress", "playwright", "puppeteer", "webdriver",
        "postman", "insomnia", "swagger", "tdd", "bdd", "ddd",
        "load testing", "performance testing", "jmeter", "locust",
        "security testing", "penetration testing", "sonarqube"
    ],
    "tools": [
        "git", "github", "gitlab", "bitbucket", "jira", "confluence",
        "notion", "slack", "figma", "sketch", "adobe xd", "invision",
        "trello", "asana", "linear", "monday", "clickup",
        "vscode", "intellij", "pycharm", "vim", "neovim",
        "postman", "docker desktop", "lens", "tableplus", "dbeaver"
    ],
    "architecture": [
        "system design", "microservices", "monolith", "serverless",
        "event sourcing", "cqrs", "domain driven design", "clean architecture",
        "mvc", "mvvm", "repository pattern", "factory pattern", "singleton",
        "api gateway", "service mesh", "load balancer", "cdn",
        "caching", "distributed systems", "cap theorem", "acid",
        "eventual consistency", "saga pattern", "circuit breaker"
    ],
    "soft_skills": [
        "leadership", "communication", "teamwork", "problem solving",
        "project management", "mentoring", "agile", "scrum", "kanban",
        "time management", "critical thinking", "adaptability",
        "collaboration", "presentation", "documentation", "code review"
    ]
}

ROLE_SKILL_MAPPING = {
    "Frontend Developer": ["react", "angular", "vue", "javascript", "typescript", "html", "css", "nextjs"],
    "Backend Developer": ["python", "java", "nodejs", "django", "fastapi", "postgresql", "redis", "rest api"],
    "Full Stack Developer": ["react", "nodejs", "python", "javascript", "postgresql", "docker", "git"],
    "DevOps Engineer": ["docker", "kubernetes", "aws", "terraform", "jenkins", "linux", "ci/cd", "ansible"],
    "Data Scientist": ["python", "machine learning", "pandas", "numpy", "tensorflow", "sql", "statistics"],
    "Machine Learning Engineer": ["pytorch", "tensorflow", "python", "mlflow", "docker", "kubernetes", "deep learning"],
    "Mobile Developer": ["react native", "flutter", "android", "ios", "swift", "kotlin", "firebase"],
    "Cloud Engineer": ["aws", "azure", "gcp", "terraform", "kubernetes", "docker", "networking"],
    "Security Engineer": ["security testing", "penetration testing", "encryption", "authentication", "linux"],
    "Data Engineer": ["spark", "hadoop", "airflow", "dbt", "sql", "python", "etl", "kafka"],
    "QA Engineer": ["selenium", "cypress", "pytest", "jest", "tdd", "bdd", "postman", "jmeter"],
    "Software Architect": ["system design", "microservices", "cloud", "distributed systems", "api gateway"],
    "Product Manager": ["agile", "scrum", "jira", "product management", "analytics", "roadmap"],
    "Software Developer": ["python", "java", "javascript", "git", "sql", "api", "testing"]
}

INTERVIEW_QA_PAIRS = {
    "python": [
        {
            "question": "What is the difference between a list and a tuple in Python?",
            "ideal_keywords": ["mutable", "immutable", "list", "tuple", "performance", "hashable"],
            "ideal_answer_points": [
                "Lists are mutable, tuples are immutable",
                "Tuples are faster and use less memory",
                "Tuples can be used as dictionary keys",
                "Lists have more built-in methods"
            ]
        },
        {
            "question": "Explain Python decorators with an example.",
            "ideal_keywords": ["wrapper", "function", "closure", "higher order", "@", "syntactic sugar"],
            "ideal_answer_points": [
                "Decorators modify function behavior without changing its source",
                "They use the @ symbol as syntactic sugar",
                "They are higher-order functions returning a wrapper",
                "Common uses: logging, authentication, caching"
            ]
        }
    ],
    "react": [
        {
            "question": "What is the virtual DOM and how does React use it?",
            "ideal_keywords": ["virtual", "dom", "reconciliation", "diffing", "performance", "update"],
            "ideal_answer_points": [
                "Virtual DOM is a lightweight copy of the real DOM",
                "React compares virtual DOM with previous version (diffing)",
                "Only changed elements are updated in real DOM (reconciliation)",
                "This makes updates faster than direct DOM manipulation"
            ]
        }
    ],
    "system_design": [
        {
            "question": "How would you design a URL shortening service like bit.ly?",
            "ideal_keywords": ["database", "hashing", "cache", "load balancer", "cdn", "scale", "api"],
            "ideal_answer_points": [
                "Generate unique short codes using hashing or base62 encoding",
                "Store mapping in database with expiry",
                "Use Redis cache for frequently accessed URLs",
                "Handle redirects with 301/302 status codes",
                "Consider rate limiting and analytics"
            ]
        }
    ]
}
