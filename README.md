<h1 align="center">🥦EnjoyFitness AI</h1>
<h3 align="center">An Open-source AI-driven dietary health solutions.</h3>
![Static Badge](https://img.shields.io/badge/release-demo-blueviolet)




## Feature

- Simple, efficient health solutions.
- Accurately measure food calories.
- Personalised health guidance based on dietary data.
- Supports end-side M-LLM deployment.



## Project Progress

|      | Programming | Code Review | Release                                                      |
| ---- | ----------- | ----------- | ------------------------------------------------------------ |
| Demo | ✅           | ✅           | ✅  [Try it !](https://github.com/EnjoyCloudDev/enjoy-fitness-ai/tree/main/demo) |
| API  | ✅           | ✅           | Comming soon !                                               |
| App  | ✅           | 👨‍💻          | 👨‍💻                                                           |



## Try Demo

We recommend using Docker to deploy the demo application.

1. Clone repository

   ```shell
   git clone https://github.com/EnjoyCloudDev/enjoy-fitness-ai.git
   ```

2. Configuring .env files

   ```shell
   $cd demo/
   $nano .env
   
   OPENAI_API_KEY = "YOUR_API_KEY"
   OPENAI_API_BASE = "YOUR_API_URL"
   BASE_MODEL = "YOUR_MODEL_NAME"
   ```

3. Build docker image

   ```shell
   docker build -t enjoyfitness_demo:latest .
   ```

4. Run

   ```shell
   docker run -d --name enjoyfitness-api --env-file .env -p 7860:7860 enjoyfitness_demo:latest
   ```

   
