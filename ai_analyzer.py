"""
AI-Powered Analysis Module using Mistral API
Enhanced client analysis and scoring with AI capabilities
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple
from mistralai import Mistral
import time
from colorama import init, Fore, Style

# Initialize colorama
init()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MistralAnalyzer:
    def __init__(self, api_key: str, model: str = "mistral-large-latest"):
        """Initialize Mistral AI client"""
        try:
            self.client = Mistral(api_key=api_key)
            self.model = model
            self.rate_limit_delay = 1  # Delay between API calls
            logger.info(f"{Fore.GREEN}✓ Mistral AI client initialized successfully{Style.RESET_ALL}")
        except Exception as e:
            logger.error(f"{Fore.RED}✗ Failed to initialize Mistral AI: {e}{Style.RESET_ALL}")
            raise
    
    def analyze_client_potential(self, post_data: Dict) -> Dict:
        """Analyze a Reddit post for client potential using AI"""
        try:
            # Prepare the content for analysis
            content = f"""
Title: {post_data.get('title', '')}
Content: {post_data.get('content', '')}
Subreddit: {post_data.get('subreddit', '')}
Author: {post_data.get('author', '')}
Score: {post_data.get('score', 0)}
Comments: {post_data.get('comments', 0)}
URL: {post_data.get('url', '')}
"""
            
            # Create the analysis prompt
            prompt = f"""
You are an expert business development analyst specializing in identifying potential clients for digital marketing, website development, and business automation services.

Analyze the following Reddit post and provide a comprehensive assessment:

{content}

Please provide your analysis in the following JSON format:
{{
    "client_potential_score": <integer 0-100>,
    "services_needed": ["list of specific services"],
    "budget_indicators": {{
        "has_budget_mention": <boolean>,
        "budget_range": "<estimated range or specific amount>",
        "budget_confidence": "<low/medium/high>"
    }},
    "urgency_level": "<low/medium/high>",
    "business_maturity": "<startup/small_business/established/large_corporation>",
    "decision_maker": <boolean>,
    "contact_readiness": "<low/medium/high>",
    "key_insights": ["list of important insights"],
    "recommended_approach": "<suggested outreach strategy>",
    "red_flags": ["list of any concerns or red flags"],
    "opportunity_summary": "<brief summary of the opportunity>"
}}

Focus on:
1. Genuine business need vs. just asking for advice
2. Budget capacity and willingness to pay
3. Timeline urgency
4. Decision-making authority
5. Business size and maturity
6. Specific service requirements
7. Contact information availability
8. Overall professionalism and seriousness

Be thorough but concise in your analysis.
"""
            
            # Make API call
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=0.3,  # Lower temperature for more consistent analysis
                max_tokens=1000
            )
            
            # Parse the response
            analysis_text = response.choices[0].message.content
            
            # Try to extract JSON from the response
            try:
                # Find JSON in the response
                start_idx = analysis_text.find('{')
                end_idx = analysis_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = analysis_text[start_idx:end_idx]
                    analysis = json.loads(json_str)
                else:
                    raise ValueError("No JSON found in response")
            except (json.JSONDecodeError, ValueError) as e:
                logger.warning(f"Failed to parse AI response as JSON: {e}")
                # Fallback analysis
                analysis = self._create_fallback_analysis(analysis_text, post_data)
            
            # Add metadata
            analysis['ai_analysis_timestamp'] = time.time()
            analysis['ai_model_used'] = self.model
            
            # Rate limiting
            time.sleep(self.rate_limit_delay)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in AI analysis: {e}")
            return self._create_fallback_analysis("", post_data)
    
    def _create_fallback_analysis(self, analysis_text: str, post_data: Dict) -> Dict:
        """Create a fallback analysis when AI parsing fails"""
        return {
            "client_potential_score": 50,
            "services_needed": ["Unknown"],
            "budget_indicators": {
                "has_budget_mention": False,
                "budget_range": "Unknown",
                "budget_confidence": "low"
            },
            "urgency_level": "medium",
            "business_maturity": "unknown",
            "decision_maker": False,
            "contact_readiness": "medium",
            "key_insights": ["AI analysis failed - manual review needed"],
            "recommended_approach": "Standard outreach",
            "red_flags": ["AI analysis unavailable"],
            "opportunity_summary": "Requires manual review",
            "ai_analysis_timestamp": time.time(),
            "ai_model_used": "fallback",
            "raw_analysis": analysis_text
        }
    
    def generate_client_summary(self, post_data: Dict, ai_analysis: Dict) -> str:
        """Generate a comprehensive client summary"""
        try:
            prompt = f"""
Based on the following Reddit post and AI analysis, create a professional client summary for a business development team:

POST DATA:
Title: {post_data.get('title', '')}
Content: {post_data.get('content', '')}
Subreddit: r/{post_data.get('subreddit', '')}
Engagement: {post_data.get('score', 0)} upvotes, {post_data.get('comments', 0)} comments
URL: {post_data.get('url', '')}

AI ANALYSIS:
{json.dumps(ai_analysis, indent=2)}

Create a professional summary that includes:
1. Executive summary of the opportunity
2. Key business needs identified
3. Budget and timeline considerations
4. Recommended next steps
5. Priority level and reasoning

Format as a clear, actionable business brief.
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=0.4,
                max_tokens=800
            )
            
            summary = response.choices[0].message.content
            time.sleep(self.rate_limit_delay)
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating client summary: {e}")
            return f"Summary generation failed: {e}"
    
    def categorize_services(self, post_data: Dict) -> List[str]:
        """Use AI to categorize and identify specific services needed"""
        try:
            content = f"{post_data.get('title', '')} {post_data.get('content', '')}"
            
            prompt = f"""
Analyze this Reddit post and identify specific services the person might need:

Content: {content}

Categorize into these service areas and be specific:
- Digital Marketing (SEO, PPC, Social Media, Content Marketing, Email Marketing, etc.)
- Website Development (Custom Development, E-commerce, WordPress, Landing Pages, etc.)
- Business Automation (Workflow Automation, API Integration, Data Processing, etc.)

Return only a JSON array of specific services, like:
["SEO Optimization", "Google Ads Management", "Custom E-commerce Website"]

Be specific and practical in your categorization.
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=0.2,
                max_tokens=300
            )
            
            response_text = response.choices[0].message.content
            
            # Try to parse as JSON array
            try:
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    services = json.loads(json_str)
                else:
                    services = ["Manual Review Needed"]
            except (json.JSONDecodeError, ValueError):
                services = ["Manual Review Needed"]
            
            time.sleep(self.rate_limit_delay)
            return services
            
        except Exception as e:
            logger.error(f"Error categorizing services: {e}")
            return ["Error in AI categorization"]
    
    def extract_business_info(self, post_data: Dict) -> Dict:
        """Extract detailed business information using AI"""
        try:
            content = f"{post_data.get('title', '')} {post_data.get('content', '')}"
            
            prompt = f"""
Extract business information from this Reddit post:

Content: {content}

Return a JSON object with:
{{
    "company_name": "<extracted or inferred company name>",
    "industry": "<industry or business type>",
    "business_size": "<startup/small/medium/large>",
    "revenue_indicators": "<any revenue or financial indicators>",
    "location": "<geographic location if mentioned>",
    "business_stage": "<idea/startup/growing/established>",
    "team_size": "<team size indicators>",
    "technology_stack": "<any mentioned technologies>",
    "competitors_mentioned": ["list of competitors"],
    "market_focus": "<target market or customer base>"
}}

If information is not available, use "Unknown" or empty arrays.
"""
            
            response = self.client.chat.complete(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=500
            )
            
            response_text = response.choices[0].message.content
            
            # Try to parse JSON
            try:
                start_idx = response_text.find('{')
                end_idx = response_text.rfind('}') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    business_info = json.loads(json_str)
                else:
                    business_info = {"error": "Could not parse business info"}
            except (json.JSONDecodeError, ValueError):
                business_info = {"error": "JSON parsing failed"}
            
            time.sleep(self.rate_limit_delay)
            return business_info
            
        except Exception as e:
            logger.error(f"Error extracting business info: {e}")
            return {"error": str(e)}
    
    def generate_outreach_suggestions(self, post_data: Dict, ai_analysis: Dict) -> List[str]:
        """Generate personalized outreach suggestions"""
        try:
            prompt = f"""
Based on this Reddit post and analysis, suggest 3-5 personalized outreach approaches:

POST: {post_data.get('title', '')} - {post_data.get('content', '')[:200]}...
ANALYSIS: {json.dumps(ai_analysis, indent=2)}

Provide specific, actionable outreach suggestions that:
1. Address their specific pain points
2. Offer immediate value
3. Are personalized to their situation
4. Include specific next steps

Return as a JSON array of outreach suggestions.
"""
            
            messages = [{"role": "user", "content": prompt}]
            response = self.client.chat.complete(
                model=self.model,
                messages=messages,
                temperature=0.5,
                max_tokens=600
            )
            
            response_text = response.choices[0].message.content
            
            # Try to parse as JSON array
            try:
                start_idx = response_text.find('[')
                end_idx = response_text.rfind(']') + 1
                if start_idx != -1 and end_idx != -1:
                    json_str = response_text[start_idx:end_idx]
                    suggestions = json.loads(json_str)
                else:
                    suggestions = ["Manual outreach review needed"]
            except (json.JSONDecodeError, ValueError):
                suggestions = ["Manual outreach review needed"]
            
            time.sleep(self.rate_limit_delay)
            return suggestions
            
        except Exception as e:
            logger.error(f"Error generating outreach suggestions: {e}")
            return [f"Outreach generation failed: {e}"]


class AIEnhancedAnalyzer:
    """Main class that combines traditional analysis with AI insights"""
    
    def __init__(self, mistral_api_key: str, use_ai: bool = True):
        """Initialize the enhanced analyzer"""
        self.use_ai = use_ai
        self.ai_analyzer = None
        
        if use_ai and mistral_api_key:
            try:
                self.ai_analyzer = MistralAnalyzer(mistral_api_key)
                logger.info(f"{Fore.GREEN}✓ AI-enhanced analysis enabled{Style.RESET_ALL}")
            except Exception as e:
                logger.warning(f"{Fore.YELLOW}⚠ AI analysis disabled due to error: {e}{Style.RESET_ALL}")
                self.use_ai = False
        else:
            logger.info(f"{Fore.YELLOW}⚠ AI analysis disabled{Style.RESET_ALL}")
    
    def analyze_post(self, post_data: Dict) -> Dict:
        """Comprehensive post analysis combining traditional and AI methods"""
        analysis = {
            'traditional_analysis': self._traditional_analysis(post_data),
            'ai_analysis': None,
            'combined_score': 0,
            'ai_enhanced': False
        }
        
        if self.use_ai and self.ai_analyzer:
            try:
                # Get AI analysis
                ai_analysis = self.ai_analyzer.analyze_client_potential(post_data)
                analysis['ai_analysis'] = ai_analysis
                analysis['ai_enhanced'] = True
                
                # Generate additional AI insights
                analysis['ai_services'] = self.ai_analyzer.categorize_services(post_data)
                analysis['ai_business_info'] = self.ai_analyzer.extract_business_info(post_data)
                analysis['ai_summary'] = self.ai_analyzer.generate_client_summary(post_data, ai_analysis)
                analysis['ai_outreach'] = self.ai_analyzer.generate_outreach_suggestions(post_data, ai_analysis)
                
                # Calculate combined score
                traditional_score = analysis['traditional_analysis'].get('relevance_score', 0)
                ai_score = ai_analysis.get('client_potential_score', 0)
                analysis['combined_score'] = int((traditional_score + ai_score) / 2)
                
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")
                analysis['ai_analysis'] = {'error': str(e)}
        
        return analysis
    
    def _traditional_analysis(self, post_data: Dict) -> Dict:
        """Traditional analysis methods (fallback when AI is not available)"""
        # This would contain the original scoring logic
        # For now, return a basic structure
        return {
            'relevance_score': 50,
            'services_detected': ['Manual Review'],
            'business_context': True,
            'engagement_score': post_data.get('score', 0) + post_data.get('comments', 0)
        }
