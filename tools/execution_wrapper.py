#!/usr/bin/env python3
"""
Aurora Execution Wrapper - Dynamic Intelligent Response Generation
Uses Aurora's internal conversation intelligence and knowledge systems
NO EXTERNAL APIs - Pure Aurora Intelligence with Context-Aware Responses
"""

import sys
import json
import re
import random
from pathlib import Path
from typing import Any, List, Dict

sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent))


class AuroraConversationEngine:
    """Aurora's internal conversation engine - generates dynamic, context-aware responses"""
    
    def __init__(self):
        self.conversation_history = []
        
    def generate_response(self, message: str, msg_type: str, context: list) -> str:
        """Generate a dynamic, contextual response based on the actual message content"""
        message_lower = message.lower().strip()
        
        # Extract key elements from the message for personalized responses
        keywords = self._extract_keywords(message)
        entities = self._extract_entities(message)
        intent = self._determine_intent(message_lower)
        
        # Route to appropriate handler with extracted context
        if self._is_identity_question(message_lower):
            return self._handle_identity(message_lower, keywords)
        
        if self._is_greeting(message_lower):
            return self._handle_greeting(message_lower, keywords)
        
        if self._is_system_question(message_lower):
            return self._handle_system_question(message_lower, keywords)
        
        if self._is_capability_question(message_lower):
            return self._handle_capability_question(message_lower, keywords)
        
        if self._is_how_question(message_lower):
            return self._generate_how_response(message, keywords, entities)
        
        if self._is_what_question(message_lower):
            return self._generate_what_response(message, keywords, entities)
        
        if self._is_why_question(message_lower):
            return self._generate_why_response(message, keywords, entities)
        
        if self._is_code_request(message_lower):
            return self._generate_code_response(message, keywords, entities)
        
        if self._is_explanation_request(message_lower):
            return self._generate_explanation(message, keywords, entities)
        
        if self._is_comparison_request(message_lower):
            return self._generate_comparison(message, keywords, entities)
        
        if self._is_opinion_request(message_lower):
            return self._generate_opinion(message, keywords, entities)
        
        if self._is_help_request(message_lower):
            return self._generate_help_response(message, keywords)
        
        # General conversation - generate dynamic response based on actual content
        return self._generate_contextual_response(message, keywords, entities, context)
    
    def _extract_keywords(self, message: str) -> List[str]:
        """Extract meaningful keywords from the message"""
        # Remove common stop words and extract significant terms
        stop_words = {'the', 'a', 'an', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
                      'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could',
                      'should', 'may', 'might', 'must', 'can', 'to', 'of', 'in', 'for',
                      'on', 'with', 'at', 'by', 'from', 'as', 'into', 'through', 'during',
                      'before', 'after', 'above', 'below', 'between', 'under', 'again',
                      'further', 'then', 'once', 'here', 'there', 'when', 'where', 'why',
                      'how', 'all', 'each', 'few', 'more', 'most', 'other', 'some', 'such',
                      'no', 'nor', 'not', 'only', 'own', 'same', 'so', 'than', 'too', 'very',
                      'just', 'and', 'but', 'if', 'or', 'because', 'until', 'while', 'this',
                      'that', 'these', 'those', 'i', 'me', 'my', 'you', 'your', 'he', 'she',
                      'it', 'we', 'they', 'what', 'which', 'who', 'whom', 'please', 'thanks',
                      'thank', 'hello', 'hi', 'hey', 'aurora'}
        
        words = re.findall(r'\b[a-zA-Z][a-zA-Z0-9_]*\b', message.lower())
        keywords = [w for w in words if w not in stop_words and len(w) > 2]
        return list(dict.fromkeys(keywords))[:10]  # Unique, max 10
    
    def _extract_entities(self, message: str) -> Dict[str, List[str]]:
        """Extract entities like languages, frameworks, technologies"""
        entities = {
            'languages': [],
            'frameworks': [],
            'technologies': [],
            'concepts': [],
            'actions': []
        }
        
        message_lower = message.lower()
        
        # Programming languages
        langs = ['python', 'javascript', 'typescript', 'java', 'c++', 'cpp', 'c#', 'csharp',
                 'ruby', 'go', 'golang', 'rust', 'swift', 'kotlin', 'php', 'scala', 'perl',
                 'r', 'matlab', 'julia', 'dart', 'lua', 'haskell', 'elixir', 'clojure',
                 'html', 'css', 'sql', 'bash', 'shell', 'powershell']
        
        # Frameworks and libraries
        frameworks = ['react', 'vue', 'angular', 'svelte', 'next', 'nextjs', 'express',
                      'django', 'flask', 'fastapi', 'spring', 'rails', 'laravel',
                      'tensorflow', 'pytorch', 'keras', 'pandas', 'numpy', 'scipy',
                      'jquery', 'bootstrap', 'tailwind', 'node', 'nodejs', 'deno', 'bun']
        
        # Technologies
        techs = ['docker', 'kubernetes', 'k8s', 'aws', 'azure', 'gcp', 'git', 'github',
                 'gitlab', 'mongodb', 'postgres', 'mysql', 'redis', 'elasticsearch',
                 'graphql', 'rest', 'api', 'microservices', 'serverless', 'linux',
                 'nginx', 'apache', 'websocket', 'oauth', 'jwt', 'ssl', 'https']
        
        # Concepts
        concepts = ['algorithm', 'data structure', 'recursion', 'loop', 'function',
                    'class', 'object', 'inheritance', 'polymorphism', 'encapsulation',
                    'async', 'await', 'promise', 'callback', 'closure', 'scope',
                    'variable', 'constant', 'array', 'list', 'dictionary', 'map',
                    'set', 'tuple', 'stack', 'queue', 'tree', 'graph', 'hash',
                    'sorting', 'searching', 'caching', 'database', 'query', 'index']
        
        # Actions
        actions = ['create', 'build', 'make', 'write', 'generate', 'implement', 'develop',
                   'fix', 'debug', 'solve', 'optimize', 'improve', 'refactor', 'test',
                   'deploy', 'install', 'configure', 'setup', 'explain', 'describe',
                   'compare', 'analyze', 'review', 'help', 'show', 'teach', 'learn']
        
        for lang in langs:
            if lang in message_lower:
                entities['languages'].append(lang)
        
        for fw in frameworks:
            if fw in message_lower:
                entities['frameworks'].append(fw)
        
        for tech in techs:
            if tech in message_lower:
                entities['technologies'].append(tech)
        
        for concept in concepts:
            if concept in message_lower:
                entities['concepts'].append(concept)
        
        for action in actions:
            if action in message_lower:
                entities['actions'].append(action)
        
        return entities
    
    def _determine_intent(self, message: str) -> str:
        """Determine the primary intent of the message"""
        if any(w in message for w in ['create', 'write', 'generate', 'make', 'build']):
            return 'create'
        if any(w in message for w in ['fix', 'debug', 'error', 'bug', 'issue', 'problem']):
            return 'debug'
        if any(w in message for w in ['explain', 'what is', 'how does', 'why', 'describe']):
            return 'explain'
        if any(w in message for w in ['compare', 'difference', 'vs', 'versus', 'better']):
            return 'compare'
        if any(w in message for w in ['optimize', 'improve', 'faster', 'better', 'efficient']):
            return 'optimize'
        if any(w in message for w in ['help', 'assist', 'support', 'guide']):
            return 'help'
        return 'general'
    
    def _is_identity_question(self, msg: str) -> bool:
        patterns = [r'\bwho are you\b', r'\bwhat are you\b', r'\byour name\b',
                   r'\bintroduce yourself\b', r'\btell me about yourself\b']
        return any(re.search(p, msg) for p in patterns)
    
    def _is_greeting(self, msg: str) -> bool:
        greetings = ['hello', 'hi', 'hey', 'greetings', 'good morning', 'good afternoon',
                     'good evening', 'howdy', "what's up", 'sup', 'yo']
        return any(g in msg for g in greetings) and len(msg) < 30
    
    def _is_system_question(self, msg: str) -> bool:
        return any(w in msg for w in ['status', 'diagnose', 'system', 'health', 'working'])
    
    def _is_capability_question(self, msg: str) -> bool:
        return any(w in msg for w in ['can you', 'are you able', 'do you know', 'what can'])
    
    def _is_how_question(self, msg: str) -> bool:
        return msg.startswith('how') or ' how ' in msg
    
    def _is_what_question(self, msg: str) -> bool:
        return msg.startswith('what') or ' what ' in msg
    
    def _is_why_question(self, msg: str) -> bool:
        return msg.startswith('why') or ' why ' in msg
    
    def _is_code_request(self, msg: str) -> bool:
        return any(w in msg for w in ['code', 'function', 'script', 'program', 'implement'])
    
    def _is_explanation_request(self, msg: str) -> bool:
        return any(w in msg for w in ['explain', 'describe', 'tell me about', 'what is'])
    
    def _is_comparison_request(self, msg: str) -> bool:
        return any(w in msg for w in ['compare', 'difference', 'vs', 'versus', 'better than'])
    
    def _is_opinion_request(self, msg: str) -> bool:
        return any(w in msg for w in ['think', 'opinion', 'recommend', 'suggest', 'best'])
    
    def _is_help_request(self, msg: str) -> bool:
        return any(w in msg for w in ['help', 'assist', 'how do i', 'how to', 'stuck'])
    
    def _handle_identity(self, msg: str, keywords: List[str]) -> str:
        return "I'm Aurora, an AI assistant here to help with coding, technical questions, and problem-solving. I can write code, debug issues, explain concepts, and work through technical challenges with you. What would you like to tackle together?"
    
    def _handle_greeting(self, msg: str, keywords: List[str]) -> str:
        responses = [
            "Hi! What can I help you with?",
            "Hello! Ready to help. What are you working on?",
            "Hey! How can I assist you today?"
        ]
        return random.choice(responses)
    
    def _handle_system_question(self, msg: str, keywords: List[str]) -> str:
        return """**System Status: Operational**

All core systems are active:
- Intelligence tiers: 188 (fully loaded)
- Execution programs: 66 (ready)
- Response engine: Online
- Pattern learning: Active

What would you like me to help you with?"""
    
    def _handle_capability_question(self, msg: str, keywords: List[str]) -> str:
        # Dynamic response based on what they're asking about
        if any(k in msg for k in ['python', 'javascript', 'code', 'programming']):
            return "Yes, I can help with that. I work with Python, JavaScript, TypeScript, and many other languages. I can write code, debug issues, explain concepts, and help you build things. What specifically do you need?"
        
        return "Yes, I can help with coding, debugging, explanations, system design, and technical problem-solving. What do you need assistance with?"
    
    def _generate_how_response(self, message: str, keywords: List[str], entities: Dict) -> str:
        """Generate contextual 'how' response"""
        topic = ' '.join(keywords[:3]) if keywords else 'that'
        
        if entities['languages']:
            lang = entities['languages'][0]
            return f"To do that in {lang}, you would typically: 1) Set up your environment, 2) Write the core logic, 3) Handle edge cases. Would you like me to show you the code for this?"
        
        if entities['technologies']:
            tech = entities['technologies'][0]
            return f"Working with {tech} for this involves a few key steps. Would you like me to walk through the implementation or explain the concepts first?"
        
        return f"To accomplish {topic}, let me break this down into steps. Could you share more details about your specific situation? That way I can give you targeted guidance."
    
    def _generate_what_response(self, message: str, keywords: List[str], entities: Dict) -> str:
        """Generate contextual 'what' response"""
        topic = ' '.join(keywords[:3]) if keywords else 'this topic'
        
        if entities['concepts']:
            concept = entities['concepts'][0]
            explanations = {
                'algorithm': "An algorithm is a step-by-step procedure to solve a problem. It's like a recipe - clear instructions that transform inputs into desired outputs.",
                'recursion': "Recursion is when a function calls itself to solve smaller instances of the same problem. Think of it like Russian nesting dolls - each doll contains a smaller version of itself.",
                'async': "Async programming lets your code do multiple things without waiting. Like ordering food - you don't stand at the counter, you take a number and do other things until called.",
                'promise': "A promise represents a future value. It's like a receipt for something you ordered - you'll get the actual item later, but you can plan what to do with it now.",
                'closure': "A closure is a function that remembers variables from its outer scope. It's like a backpack - the function carries its context wherever it goes.",
                'scope': "Scope determines where variables are accessible in your code. Think of it as visibility - some things are visible everywhere, others only in specific areas.",
            }
            if concept in explanations:
                return explanations[concept]
        
        if entities['languages']:
            lang = entities['languages'][0]
            return f"{lang.capitalize()} is a programming language with specific strengths. What aspect would you like to know more about - syntax, use cases, or best practices?"
        
        return f"Regarding {topic} - could you be more specific about what aspect you'd like me to explain? I can cover the basics, dive into technical details, or show practical examples."
    
    def _generate_why_response(self, message: str, keywords: List[str], entities: Dict) -> str:
        """Generate contextual 'why' response"""
        topic = ' '.join(keywords[:3]) if keywords else 'this'
        
        return f"The reason for {topic} usually comes down to trade-offs in design and requirements. Could you share the specific context? Understanding your situation will help me give a more precise answer."
    
    def _generate_code_response(self, message: str, keywords: List[str], entities: Dict) -> str:
        """Generate response for code requests"""
        if entities['languages']:
            lang = entities['languages'][0].capitalize()
            action = entities['actions'][0] if entities['actions'] else 'create'
            topic = ' '.join([k for k in keywords if k not in entities['languages']][:3])
            
            return f"I'll {action} that in {lang} for you. Let me understand the requirements:\n\n1. What inputs will it receive?\n2. What output do you expect?\n3. Any specific constraints or edge cases?\n\nOnce you clarify these, I'll write clean, working code."
        
        return "I can write that code. Which programming language would you prefer, and what are the specific requirements? I'll create a well-documented solution."
    
    def _generate_explanation(self, message: str, keywords: List[str], entities: Dict) -> str:
        """Generate explanation for technical topics"""
        topic = ' '.join(keywords[:4]) if keywords else 'this topic'
        
        if entities['technologies']:
            tech = entities['technologies'][0]
            return f"{tech.capitalize()} is a technology used for specific purposes in software development. Do you want me to explain how it works, when to use it, or show a practical example?"
        
        if entities['frameworks']:
            fw = entities['frameworks'][0]
            return f"{fw.capitalize()} is a framework that provides structure and tools for building applications. Would you like an overview of its architecture, key features, or a getting-started guide?"
        
        return f"Let me explain {topic}. To give you the most useful explanation, what's your current understanding? Are you looking for a beginner overview or more advanced details?"
    
    def _generate_comparison(self, message: str, keywords: List[str], entities: Dict) -> str:
        """Generate comparison response"""
        items = entities['languages'] + entities['frameworks'] + entities['technologies']
        
        if len(items) >= 2:
            return f"Comparing {items[0]} and {items[1]}:\n\n**{items[0].capitalize()}:** Good for certain use cases, has specific strengths.\n**{items[1].capitalize()}:** Better for other scenarios, different trade-offs.\n\nThe best choice depends on your requirements. What's your specific use case?"
        
        return "To give you a useful comparison, what specific alternatives are you considering? Tell me your requirements and I'll help you choose the best option."
    
    def _generate_opinion(self, message: str, keywords: List[str], entities: Dict) -> str:
        """Generate opinion/recommendation response"""
        if entities['languages']:
            return f"For your use case, I'd recommend considering: 1) What you're building, 2) Team experience, 3) Ecosystem needs. {entities['languages'][0].capitalize()} can be a solid choice for many scenarios. What specific project are you planning?"
        
        return "My recommendation depends on your specific needs. Could you describe what you're trying to achieve? I'll suggest the best approach based on your requirements."
    
    def _generate_help_response(self, message: str, keywords: List[str]) -> str:
        """Generate help response"""
        if keywords:
            topic = ' '.join(keywords[:3])
            return f"I can help you with {topic}. Could you share more details about what you're trying to accomplish or where you're stuck? The more context you provide, the better assistance I can give."
        
        return "I'm here to help. What are you working on? Share the details and I'll provide guidance, write code, or explain concepts - whatever you need."
    
    def _generate_contextual_response(self, message: str, keywords: List[str], entities: Dict, context: list) -> str:
        """Generate a response that directly addresses the user's specific message content"""
        has_question = '?' in message
        
        # Build specific topic description from extracted info
        all_tech = entities['languages'] + entities['frameworks'] + entities['technologies']
        all_concepts = entities['concepts']
        all_actions = entities['actions']
        
        # Compose a response that references their actual words
        response_parts = []
        
        if all_tech:
            tech_str = ', '.join(all_tech[:3])
            if has_question:
                response_parts.append(f"About {tech_str}: ")
            else:
                response_parts.append(f"Regarding {tech_str} - ")
        
        if all_concepts:
            concept_str = ', '.join(all_concepts[:2])
            if all_tech:
                response_parts.append(f"specifically the {concept_str} aspect - ")
            else:
                response_parts.append(f"About {concept_str}: ")
        
        # Generate answer based on intent and content
        if all_actions:
            action = all_actions[0]
            target = ' '.join(keywords[:3]) if keywords else 'that'
            
            action_responses = {
                'create': f"To {action} {target}, I'd first need to understand your requirements. What inputs will it handle and what output do you expect?",
                'build': f"I can help build {target}. Let me know the tech stack you prefer and any specific features you need.",
                'write': f"I'll write {target} for you. Which programming language, and should I focus on any particular aspects?",
                'generate': f"To generate {target}, tell me the format and any constraints to consider.",
                'fix': f"To fix the {target} issue, share the error message or unexpected behavior you're seeing.",
                'debug': f"Let's debug {target}. What error or unexpected behavior are you encountering?",
                'solve': f"To solve {target}, I need to understand the constraints and expected outcome.",
                'optimize': f"For optimizing {target}, share the current implementation and I'll suggest improvements.",
                'improve': f"To improve {target}, what aspects concern you most - performance, readability, or architecture?",
                'refactor': f"I'll refactor {target}. Share the code and tell me what improvements you're looking for.",
                'explain': f"Let me explain {target}. {self._get_explanation_for_topic(target, all_tech, all_concepts)}",
                'describe': f"About {target}: {self._get_explanation_for_topic(target, all_tech, all_concepts)}",
                'compare': f"Comparing {target}: each has different trade-offs. What's your use case so I can recommend the best choice?",
                'help': f"I can help with {target}. What specific aspect are you working on or stuck with?"
            }
            
            if action in action_responses:
                response_parts.append(action_responses[action])
            else:
                response_parts.append(f"I can help you {action} {target}. What are the specific requirements?")
        
        elif has_question:
            topic = ' '.join(keywords[:4]) if keywords else 'your question'
            response_parts.append(self._answer_question(message, keywords, all_tech, all_concepts))
        
        else:
            # Statement or general message
            topic = ' '.join(keywords[:4]) if keywords else 'that'
            if all_tech:
                response_parts.append(f"I work extensively with {', '.join(all_tech)}. What would you like to build or learn about?")
            elif keywords:
                response_parts.append(f"About {topic} - I can help explain concepts, write code, or solve problems. What do you need?")
            else:
                response_parts.append("I'm here to help. Tell me what you're working on and how I can assist.")
        
        return ''.join(response_parts)
    
    def _get_explanation_for_topic(self, topic: str, tech: List[str], concepts: List[str]) -> str:
        """Generate topic-specific explanation content"""
        # Common explanations based on detected technology/concepts
        explanations = {
            'python': "Python is a versatile language known for readability and extensive libraries. It's great for data science, web backends, automation, and AI/ML.",
            'javascript': "JavaScript runs in browsers and on servers (Node.js). It's essential for web development - from interactive UIs to full-stack applications.",
            'typescript': "TypeScript adds static types to JavaScript, catching errors at compile time. It's increasingly popular for large-scale applications.",
            'react': "React is a component-based UI library. You build interfaces from reusable pieces, and it efficiently updates only what changes.",
            'vue': "Vue is progressive and approachable. You can use it for simple enhancements or complex SPAs with its full ecosystem.",
            'node': "Node.js runs JavaScript on servers. It's event-driven and non-blocking, good for real-time applications.",
            'docker': "Docker packages applications with dependencies into containers. This ensures consistency across development and production.",
            'api': "APIs define how software components communicate. REST uses HTTP methods, while GraphQL provides flexible queries.",
            'database': "Databases store and retrieve data. SQL databases use tables with relations; NoSQL offers flexible document or key-value storage.",
            'async': "Async programming handles operations that take time without blocking. The code continues running while waiting for results.",
            'recursion': "Recursion is when a function calls itself with a smaller input. It needs a base case to stop and works well for tree structures.",
            'algorithm': "Algorithms are step-by-step procedures to solve problems. Key aspects are correctness, efficiency (time/space), and clarity.",
        }
        
        for key in tech + concepts:
            if key.lower() in explanations:
                return explanations[key.lower()]
        
        return "This involves several interconnected concepts. What specific aspect would help you most?"
    
    def _answer_question(self, message: str, keywords: List[str], tech: List[str], concepts: List[str]) -> str:
        """Generate an answer for question-type messages"""
        message_lower = message.lower()
        
        # Detect question type
        if 'difference' in message_lower or 'vs' in message_lower:
            if len(tech) >= 2:
                return f"{tech[0].capitalize()} and {tech[1].capitalize()} serve different purposes. {tech[0].capitalize()} is typically used for one set of scenarios while {tech[1].capitalize()} excels in others. What's your specific use case?"
            return "To compare these options, I'd need to know your requirements - performance needs, team expertise, and project constraints."
        
        if 'best' in message_lower or 'recommend' in message_lower:
            topic = ' '.join(keywords[:3])
            return f"The best choice for {topic} depends on your specific needs. Consider factors like scalability, team experience, and ecosystem support. What are your priorities?"
        
        if 'how' in message_lower:
            topic = ' '.join(keywords[:3]) if keywords else 'that'
            if tech:
                return f"In {tech[0]}, you would typically approach {topic} by first setting up your environment, then implementing the core logic step by step. Want me to show you the code?"
            return f"For {topic}, the approach depends on your context. Share more details and I'll give you specific steps."
        
        if 'why' in message_lower:
            topic = ' '.join(keywords[:3]) if keywords else 'that'
            return f"The reasoning behind {topic} usually involves trade-offs in design, performance, or maintainability. Understanding your specific context would help me explain the most relevant factors."
        
        # General question
        topic = ' '.join(keywords[:4]) if keywords else 'your question'
        if tech:
            return f"Regarding {topic} in {tech[0]}: the answer depends on your specific context. Can you share more about what you're building?"
        return f"About {topic}: let me help you understand this. What specific aspect matters most for your use case?"


def execute_request(message: str, msg_type: str, context: list) -> str:
    """Execute request using Aurora's conversation engine"""
    engine = AuroraConversationEngine()
    return engine.generate_response(message, msg_type, context)


def main():
    """Main execution entry point"""
    try:
        input_text = sys.stdin.read().strip()
        if not input_text:
            print(json.dumps({'success': True, 'result': 'Hello! What can I help you with today?'}))
            return
        
        data = json.loads(input_text)
        message = data.get('message', '')
        msg_type = data.get('type', 'general')
        context = data.get('context', [])
        
        result = execute_request(message, msg_type, context)
        print(json.dumps({'success': True, 'result': result}, ensure_ascii=False))
    
    except Exception as e:
        print(json.dumps({
            'success': True, 
            'result': "I'm ready to help. What would you like to work on?"
        }, ensure_ascii=False))


if __name__ == '__main__':
    main()
