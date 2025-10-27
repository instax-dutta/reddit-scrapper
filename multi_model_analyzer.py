"""
Multi-Model AI Analyzer
Supports multiple AI providers with automatic fallback to avoid rate limits
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


class MultiModelAnalyzer:
    def __init__(self, ai_models: List[Dict]):
        """Initialize multi-model AI analyzer with fallback support"""
        self.ai_models = [model for model in ai_models if model.get('enabled', False)]
        self.current_model_index = 0
        self.model_clients = {}
        self.rate_limit_tracker = {}
        
        # Initialize clients for each enabled model
        self._initialize_clients()
        
        if self.model_clients:
            logger.info(f"{Fore.GREEN}✓ Multi-model AI analyzer initialized with {len(self.model_clients)} providers{Style.RESET_ALL}")
        else:
            logger.warning(f"{Fore.YELLOW}⚠ No AI models available - AI analysis disabled{Style.RESET_ALL}")
    
    def _initialize_clients(self):
        """Initialize clients for each AI provider"""
        for model_config in self.ai_models:
            provider = model_config['provider']
            api_key = model_config['api_key']
            model_name = model_config['model']
            
            try:
                if provider == 'mistral':
                    from mistralai import Mistral
                    self.model_clients[provider] = {
                        'client': Mistral(api_key=api_key),
                        'model': model_name,
                        'config': model_config
                    }
                    logger.info(f"{Fore.GREEN}✓ Mistral AI client initialized{Style.RESET_ALL}")
                
                elif provider == 'openai':
                    from openai import OpenAI
                    self.model_clients[provider] = {
                        'client': OpenAI(api_key=api_key),
                        'model': model_name,
                        'config': model_config
                    }
                    logger.info(f"{Fore.GREEN}✓ OpenAI client initialized{Style.RESET_ALL}")
                
                elif provider == 'anthropic':
                    from anthropic import Anthropic
                    self.model_clients[provider] = {
                        'client': Anthropic(api_key=api_key),
                        'model': model_name,
                        'config': model_config
                    }
                    logger.info(f"{Fore.GREEN}✓ Anthropic client initialized{Style.RESET_ALL}")
                
                # Initialize rate limit tracker
                self.rate_limit_tracker[provider] = {
                    'last_request': 0,
                    'request_count': 0,
                    'rate_limited_until': 0
                }
                
            except Exception as e:
                logger.error(f"{Fore.RED}✗ Failed to initialize {provider}: {e}{Style.RESET_ALL}")
    
    def _get_available_provider(self) -> Optional[str]:
        """Get the next available provider that's not rate limited"""
        current_time = time.time()
        
        # Check if current provider is available
        for provider in list(self.model_clients.keys()):
            rate_info = self.rate_limit_tracker.get(provider, {})
            
            # Skip if rate limited
            if current_time < rate_info.get('rate_limited_until', 0):
                continue
            
            # Skip if too many recent requests (basic rate limiting)
            if current_time - rate_info.get('last_request', 0) < 1:  # 1 second between requests
                continue
            
            return provider
        
        # If no provider is immediately available, wait and try again
        if self.model_clients:
            min_wait = min(
                max(0, rate_info.get('rate_limited_until', 0) - current_time)
                for rate_info in self.rate_limit_tracker.values()
            )
            if min_wait > 0:
                logger.info(f"{Fore.YELLOW}⏳ Waiting {min_wait:.1f}s for rate limit reset{Style.RESET_ALL}")
                time.sleep(min_wait)
                return self._get_available_provider()
        
        return None
    
    def _make_api_call(self, provider: str, prompt: str) -> Optional[str]:
        """Make API call to specific provider"""
        if provider not in self.model_clients:
            return None
        
        client_info = self.model_clients[provider]
        client = client_info['client']
        model = client_info['model']
        
        try:
            # Update rate limit tracker
            current_time = time.time()
            self.rate_limit_tracker[provider]['last_request'] = current_time
            self.rate_limit_tracker[provider]['request_count'] += 1
            
            if provider == 'mistral':
                response = client.chat.complete(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            
            elif provider == 'openai':
                response = client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.3,
                    max_tokens=1000
                )
                return response.choices[0].message.content
            
            elif provider == 'anthropic':
                response = client.messages.create(
                    model=model,
                    max_tokens=1000,
                    temperature=0.3,
                    messages=[{"role": "user", "content": prompt}]
                )
                return response.content[0].text
            
        except Exception as e:
            error_msg = str(e).lower()
            
            # Handle rate limiting
            if 'rate limit' in error_msg or '429' in error_msg or 'capacity exceeded' in error_msg:
                logger.warning(f"{Fore.YELLOW}⚠ {provider} rate limited, will retry later{Style.RESET_ALL}")
                # Set rate limit cooldown (5 minutes)
                self.rate_limit_tracker[provider]['rate_limited_until'] = current_time + 300
                return None
            
            logger.error(f"{Fore.RED}✗ {provider} API error: {e}{Style.RESET_ALL}")
            return None
        
        return None
    
    def analyze_client_potential(self, post_data: Dict) -> Dict:
        """Analyze a Reddit post for client potential using available AI models"""
        if not self.model_clients:
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
        
        # Try each available provider until one succeeds
        for attempt in range(len(self.model_clients)):
            provider = self._get_available_provider()
            if not provider:
                logger.warning(f"{Fore.YELLOW}⚠ No available AI providers, skipping analysis{Style.RESET_ALL}")
                break
            
            logger.info(f"{Fore.CYAN}🤖 Using {provider} for AI analysis{Style.RESET_ALL}")
            
            response_text = self._make_api_call(provider, prompt)
            if response_text:
                try:
                    # Try to parse JSON response
                    analysis = json.loads(response_text)
                    logger.info(f"{Fore.GREEN}✓ AI analysis completed using {provider}{Style.RESET_ALL}")
                    return analysis
                except json.JSONDecodeError as e:
                    logger.warning(f"{Fore.YELLOW}⚠ Failed to parse {provider} response as JSON: {e}{Style.RESET_ALL}")
                    # Try to extract JSON from response
                    try:
                        # Look for JSON-like content in the response
                        start_idx = response_text.find('{')
                        end_idx = response_text.rfind('}') + 1
                        if start_idx != -1 and end_idx > start_idx:
                            json_text = response_text[start_idx:end_idx]
                            analysis = json.loads(json_text)
                            logger.info(f"{Fore.GREEN}✓ AI analysis completed using {provider} (extracted JSON){Style.RESET_ALL}")
                            return analysis
                    except:
                        pass
                    
                    # If JSON parsing fails, create a basic analysis
                    logger.warning(f"{Fore.YELLOW}⚠ Using fallback analysis for {provider}{Style.RESET_ALL}")
                    return self._create_fallback_analysis(response_text, provider)
            
            # If this provider failed, try the next one
            logger.info(f"{Fore.YELLOW}⚠ {provider} failed, trying next provider{Style.RESET_ALL}")
        
        # If all providers failed, return empty analysis
        logger.error(f"{Fore.RED}✗ All AI providers failed{Style.RESET_ALL}")
        return {}
    
    def _create_fallback_analysis(self, response_text: str, provider: str) -> Dict:
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
            "key_insights": [f"Analysis by {provider} (fallback mode)"],
            "recommended_services": ["digital_marketing"],
            "next_steps": "Manual review recommended"
        }
    
    def extract_business_info(self, post_data: Dict) -> Dict:
        """Extract business information using AI analysis"""
        if not self.model_clients:
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
        
        # Try each available provider
        for attempt in range(len(self.model_clients)):
            provider = self._get_available_provider()
            if not provider:
                break
            
            response_text = self._make_api_call(provider, prompt)
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
        """Get current status of all AI models"""
        status = {
            'total_models': len(self.model_clients),
            'available_models': [],
            'rate_limited_models': [],
            'model_stats': {}
        }
        
        current_time = time.time()
        
        for provider, client_info in self.model_clients.items():
            rate_info = self.rate_limit_tracker.get(provider, {})
            
            model_status = {
                'provider': provider,
                'model': client_info['model'],
                'last_request': rate_info.get('last_request', 0),
                'request_count': rate_info.get('request_count', 0),
                'rate_limited_until': rate_info.get('rate_limited_until', 0)
            }
            
            if current_time < rate_info.get('rate_limited_until', 0):
                status['rate_limited_models'].append(provider)
            else:
                status['available_models'].append(provider)
            
            status['model_stats'][provider] = model_status
        
        return status
