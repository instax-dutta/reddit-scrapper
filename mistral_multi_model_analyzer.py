"""
Mistral Multi-Model Analyzer
Uses multiple Mistral AI models with automatic fallback to avoid model-specific rate limits
"""

import os
import json
import logging
from typing import Dict, List, Optional, Tuple, Any
import time
from colorama import init, Fore, Style

# Initialize colorama
init()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MistralMultiModelAnalyzer:
    def __init__(self, mistral_api_key: str, mistral_models: List[Dict]):
        """Initialize Mistral multi-model analyzer with fallback support"""
        self.api_key = mistral_api_key
        self.mistral_models = sorted(mistral_models, key=lambda x: x.get('priority', 999))
        self.current_model_index = 0
        self.client = None
        self.model_rate_limits = {}
        
        # Initialize Mistral client
        self._initialize_client()
        
        if self.client:
            logger.info(f"{Fore.GREEN}✓ Mistral multi-model analyzer initialized with {len(self.mistral_models)} models{Style.RESET_ALL}")
            for model in self.mistral_models:
                logger.info(f"  • {model['name']} - {model['description']}")
        else:
            logger.warning(f"{Fore.YELLOW}⚠ Failed to initialize Mistral client - AI analysis disabled{Style.RESET_ALL}")
    
    def _initialize_client(self):
        """Initialize Mistral AI client"""
        try:
            from mistralai import Mistral
            self.client = Mistral(api_key=self.api_key)
            logger.info(f"{Fore.GREEN}✓ Mistral AI client initialized successfully{Style.RESET_ALL}")
            
            # Initialize rate limit tracker for each model
            for model in self.mistral_models:
                self.model_rate_limits[model['name']] = {
                    'last_request': 0,
                    'request_count': 0,
                    'rate_limited_until': 0,
                    'consecutive_failures': 0,
                    'total_requests': 0,
                    'successful_requests': 0
                }
                
        except Exception as e:
            logger.error(f"{Fore.RED}✗ Failed to initialize Mistral AI: {e}{Style.RESET_ALL}")
            self.client = None
    
    def _get_available_model(self) -> Optional[Dict]:
        """Get the next available model that's not rate limited"""
        current_time = time.time()
        
        # Try models in priority order
        for model in self.mistral_models:
            model_name = model['name']
            rate_info = self.model_rate_limits.get(model_name, {})
            
            # Skip if rate limited
            if current_time < rate_info.get('rate_limited_until', 0):
                continue
            
            # Skip if too many consecutive failures
            if rate_info.get('consecutive_failures', 0) >= 3:
                continue
            
            # Skip if too many recent requests (basic rate limiting)
            if current_time - rate_info.get('last_request', 0) < 0.5:  # 500ms between requests
                continue
            
            return model
        
        # If no model is immediately available, wait and try again
        if self.mistral_models:
            min_wait = min(
                max(0, rate_info.get('rate_limited_until', 0) - current_time)
                for rate_info in self.model_rate_limits.values()
            )
            if min_wait > 0:
                logger.info(f"{Fore.YELLOW}⏳ Waiting {min_wait:.1f}s for rate limit reset{Style.RESET_ALL}")
                time.sleep(min_wait)
                return self._get_available_model()
        
        return None
    
    def _make_api_call(self, model: Dict, prompt: str) -> Optional[str]:
        """Make API call to specific Mistral model"""
        if not self.client:
            return None
        
        model_name = model['name']
        
        try:
            # Update rate limit tracker
            current_time = time.time()
            rate_info = self.model_rate_limits[model_name]
            rate_info['last_request'] = current_time
            rate_info['request_count'] += 1
            rate_info['total_requests'] += 1
            
            logger.info(f"{Fore.CYAN}🤖 Using Mistral model: {model_name}{Style.RESET_ALL}")
            
            response = self.client.chat.complete(
                model=model_name,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=1000
            )
            
            # Mark as successful
            rate_info['successful_requests'] += 1
            rate_info['consecutive_failures'] = 0
            
            return response.choices[0].message.content
            
        except Exception as e:
            error_msg = str(e).lower()
            rate_info = self.model_rate_limits[model_name]
            rate_info['consecutive_failures'] += 1
            
            # Handle rate limiting
            if 'rate limit' in error_msg or '429' in error_msg or 'capacity exceeded' in error_msg:
                logger.warning(f"{Fore.YELLOW}⚠ {model_name} rate limited, will retry later{Style.RESET_ALL}")
                # Set rate limit cooldown (2 minutes for model-specific limits)
                rate_info['rate_limited_until'] = current_time + 120
                return None
            
            # Handle other errors
            logger.error(f"{Fore.RED}✗ {model_name} API error: {e}{Style.RESET_ALL}")
            
            # For non-rate-limit errors, shorter cooldown
            if rate_info['consecutive_failures'] >= 2:
                rate_info['rate_limited_until'] = current_time + 30
            
            return None
    
    def analyze_client_potential(self, post_data: Dict) -> Dict:
        """Analyze a Reddit post for client potential using available Mistral models"""
        if not self.client:
            return {}
        
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

Analyze this Reddit post and provide a JSON response with the following structure:

{{
    "client_potential_score": 85,
    "decision_maker": true,
    "contact_readiness": "high",
    "budget_indicators": {{
        "budget_range": "$5,000-$15,000",
        "urgency": "high"
    }},
    "business_maturity": "established",
    "industry": "e-commerce",
    "urgency_level": "high",
    "key_insights": [
        "Looking for immediate help with marketing",
        "Has budget allocated for services",
        "Decision maker actively seeking solutions"
    ],
    "recommended_services": ["digital_marketing", "website_development"],
    "next_steps": "Direct outreach with case studies"
}}

Post to analyze:
{content}

Provide a detailed analysis focusing on:
1. Client potential score (0-100)
2. Whether they're a decision maker
3. Contact readiness level
4. Budget indicators and urgency
5. Business maturity and industry
6. Key insights and recommended services
7. Suggested next steps

If information is not available, use "Unknown" or empty arrays.
"""
        
        # Try each available model until one succeeds
        for attempt in range(len(self.mistral_models)):
            model = self._get_available_model()
            if not model:
                logger.warning(f"{Fore.YELLOW}⚠ No available Mistral models, skipping analysis{Style.RESET_ALL}")
                break
            
            response_text = self._make_api_call(model, prompt)
            if response_text:
                try:
                    # Try to parse JSON response
                    analysis = json.loads(response_text)
                    logger.info(f"{Fore.GREEN}✓ AI analysis completed using {model['name']}{Style.RESET_ALL}")
                    return analysis
                except json.JSONDecodeError as e:
                    logger.warning(f"{Fore.YELLOW}⚠ Failed to parse {model['name']} response as JSON: {e}{Style.RESET_ALL}")
                    # Try to extract JSON from response
                    try:
                        # Look for JSON-like content in the response
                        start_idx = response_text.find('{')
                        end_idx = response_text.rfind('}') + 1
                        if start_idx != -1 and end_idx > start_idx:
                            json_text = response_text[start_idx:end_idx]
                            analysis = json.loads(json_text)
                            logger.info(f"{Fore.GREEN}✓ AI analysis completed using {model['name']} (extracted JSON){Style.RESET_ALL}")
                            return analysis
                    except:
                        pass
                    
                    # If JSON parsing fails, create a basic analysis
                    logger.warning(f"{Fore.YELLOW}⚠ Using fallback analysis for {model['name']}{Style.RESET_ALL}")
                    return self._create_fallback_analysis(response_text, model['name'])
            
            # If this model failed, try the next one
            logger.info(f"{Fore.YELLOW}⚠ {model['name']} failed, trying next model{Style.RESET_ALL}")
        
        # If all models failed, return empty analysis
        logger.error(f"{Fore.RED}✗ All Mistral models failed{Style.RESET_ALL}")
        return {}
    
    def _create_fallback_analysis(self, response_text: str, model_name: str) -> Dict:
        """Create a fallback analysis when JSON parsing fails"""
        # Basic keyword-based analysis
        text_lower = response_text.lower()
        
        score = 50  # Default score
        
        # Adjust score based on keywords
        if any(word in text_lower for word in ['urgent', 'asap', 'immediately', 'help needed']):
            score += 20
        if any(word in text_lower for word in ['budget', 'money', 'invest', 'pay']):
            score += 15
        if any(word in text_lower for word in ['business', 'company', 'startup', 'entrepreneur']):
            score += 10
        if any(word in text_lower for word in ['marketing', 'website', 'automation', 'development']):
            score += 15
        
        return {
            "client_potential_score": min(100, score),
            "decision_maker": "decision" in text_lower or "owner" in text_lower,
            "contact_readiness": "high" if score > 70 else "medium" if score > 50 else "low",
            "budget_indicators": {
                "budget_range": "Unknown",
                "urgency": "high" if "urgent" in text_lower else "medium"
            },
            "business_maturity": "Unknown",
            "industry": "Unknown",
            "urgency_level": "high" if "urgent" in text_lower else "medium",
            "key_insights": [f"Analysis by {model_name} (fallback mode)"],
            "recommended_services": ["digital_marketing"],
            "next_steps": "Manual review recommended"
        }
    
    def extract_business_info(self, post_data: Dict) -> Dict:
        """Extract business information using AI analysis"""
        if not self.client:
            return {}
        
        content = f"""
Title: {post_data.get('title', '')}
Content: {post_data.get('content', '')}
Subreddit: {post_data.get('subreddit', '')}
"""
        
        prompt = f"""
Extract business information from this Reddit post and return a JSON response:

{{
    "business_type": "e-commerce",
    "industry": "retail",
    "company_size": "small",
    "revenue_range": "$100k-$500k",
    "location": "United States",
    "contact_methods": ["email", "phone"],
    "pain_points": ["low conversion rates", "poor website performance"],
    "goals": ["increase sales", "improve marketing"]
}}

Post content:
{content}

Extract relevant business information. If information is not available, use "Unknown".
"""
        
        # Try each available model
        for attempt in range(len(self.mistral_models)):
            model = self._get_available_model()
            if not model:
                break
            
            response_text = self._make_api_call(model, prompt)
            if response_text:
                try:
                    analysis = json.loads(response_text)
                    return analysis
                except json.JSONDecodeError:
                    # Try to extract JSON
                    try:
                        start_idx = response_text.find('{')
                        end_idx = response_text.rfind('}') + 1
                        if start_idx != -1 and end_idx > start_idx:
                            json_text = response_text[start_idx:end_idx]
                            analysis = json.loads(json_text)
                            return analysis
                    except:
                        pass
        
        return {}
    
    def get_status(self) -> Dict:
        """Get current status of all Mistral models"""
        status = {
            'total_models': len(self.mistral_models),
            'available_models': [],
            'rate_limited_models': [],
            'model_stats': {}
        }
        
        current_time = time.time()
        
        for model in self.mistral_models:
            model_name = model['name']
            rate_info = self.model_rate_limits.get(model_name, {})
            
            model_status = {
                'name': model_name,
                'description': model['description'],
                'priority': model['priority'],
                'last_request': rate_info.get('last_request', 0),
                'total_requests': rate_info.get('total_requests', 0),
                'successful_requests': rate_info.get('successful_requests', 0),
                'success_rate': (rate_info.get('successful_requests', 0) / max(1, rate_info.get('total_requests', 1))) * 100,
                'consecutive_failures': rate_info.get('consecutive_failures', 0),
                'rate_limited_until': rate_info.get('rate_limited_until', 0)
            }
            
            if current_time < rate_info.get('rate_limited_until', 0):
                status['rate_limited_models'].append(model_name)
            else:
                status['available_models'].append(model_name)
            
            status['model_stats'][model_name] = model_status
        
        return status
    
    def reset_model_limits(self, model_name: str = None):
        """Reset rate limits for a specific model or all models"""
        if model_name:
            if model_name in self.model_rate_limits:
                self.model_rate_limits[model_name]['rate_limited_until'] = 0
                self.model_rate_limits[model_name]['consecutive_failures'] = 0
                logger.info(f"{Fore.GREEN}✓ Reset rate limits for {model_name}{Style.RESET_ALL}")
        else:
            for model in self.model_rate_limits:
                self.model_rate_limits[model]['rate_limited_until'] = 0
                self.model_rate_limits[model]['consecutive_failures'] = 0
            logger.info(f"{Fore.GREEN}✓ Reset rate limits for all models{Style.RESET_ALL}")
