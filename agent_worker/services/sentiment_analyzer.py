from typing import List, Optional, Dict, Tuple
from datetime import datetime, timedelta
try:
    from ..models.schemas import (
        Interaction, SentimentLevel, BugType, BugReport,
        ActionType, FinishReason
    )
except ImportError:
    from models.schemas import (
        Interaction, SentimentLevel, BugType, BugReport,
        ActionType, FinishReason
    )


class SentimentAnalyzer:
    def __init__(self):
        self.error_patterns = {
            "404": BugType.NAVIGATION_ERROR,
            "error": BugType.UNKNOWN,
            "failed": BugType.INTERACTION_FAILURE,
            "timeout": BugType.LOADING_ERROR,
            "not found": BugType.UI_ERROR,
            "invalid": BugType.VALIDATION_ERROR,
            "cannot": BugType.INTERACTION_FAILURE,
            "unable": BugType.INTERACTION_FAILURE,
            "selector_not_found": BugType.INTERACTION_FAILURE,
            "no_target_provided": BugType.INTERACTION_FAILURE,
            "selector_failed": BugType.INTERACTION_FAILURE,
            "fill_failed": BugType.INTERACTION_FAILURE,
            "click_failed": BugType.INTERACTION_FAILURE,
            "unexpected_error": BugType.UNKNOWN,
        }
        
        self.frustration_indicators = [
            "multiple clicks",
            "repeated actions",
            "backtracking",
            "error recovery",
            "slow loading",
        ]
        
    def analyze_sentiment(
        self, 
        interactions: List[Interaction], 
        current_step: int,
        persona_bio: str
    ) -> Tuple[SentimentLevel, Optional[str]]:
        """Analyze user sentiment based on recent interactions."""
        if not interactions:
            return SentimentLevel.NEUTRAL, None
            
        recent_interactions = interactions[-5:]  # Look at last 5 interactions
        
        error_count = sum(1 for i in recent_interactions if i.bug_detected)
        repeated_actions = self._detect_repeated_actions(recent_interactions)
        time_spent = self._calculate_time_spent(recent_interactions)
        
        sentiment = SentimentLevel.NEUTRAL
        feeling = None
        
        # Check for actual progress/success
        successful_actions = sum(1 for i in recent_interactions if self._is_meaningful_progress(i))
        
        # Check for navigation/visibility issues
        navigation_failures = sum(1 for i in recent_interactions 
                                if "selector_not_found" in i.result or 
                                   "no_target_provided" in i.result or
                                   "click_failed" in i.result)
        
        # Check if agent is just scrolling without progress
        only_scrolling = all(i.action_type == ActionType.SCROLL for i in recent_interactions[-3:]) if len(recent_interactions) >= 3 else False
        
        if error_count >= 3 or navigation_failures >= 3:
            sentiment = SentimentLevel.FRUSTRATED
            feeling = "The user seems frustrated due to multiple errors or inability to interact with the site"
        elif error_count >= 2 or navigation_failures >= 2:
            sentiment = SentimentLevel.NEGATIVE
            feeling = "The user is experiencing some difficulties navigating or interacting"
        elif repeated_actions > 2:
            sentiment = SentimentLevel.NEGATIVE
            feeling = "The user appears confused, repeating similar actions"
        elif only_scrolling and successful_actions == 0:
            sentiment = SentimentLevel.NEGATIVE
            feeling = "The user seems lost, just scrolling without finding anything useful"
        elif time_spent > timedelta(seconds=30) and successful_actions == 0:
            sentiment = SentimentLevel.NEGATIVE
            feeling = "The user is spending too much time on a simple task"
        elif (error_count >= 1 or navigation_failures >= 1) and successful_actions == 0:
            sentiment = SentimentLevel.NEGATIVE
            feeling = "The user is having trouble interacting with the site"
        elif successful_actions >= 2 and error_count == 0 and navigation_failures == 0:
            sentiment = SentimentLevel.POSITIVE
            feeling = "The user is progressing smoothly"
        elif successful_actions >= 1 and (error_count + navigation_failures) <= 1:
            sentiment = SentimentLevel.POSITIVE
            feeling = "The user is making progress despite minor issues"
            
        if self._check_persona_interest(interactions, persona_bio):
            if sentiment == SentimentLevel.POSITIVE:
                sentiment = SentimentLevel.VERY_POSITIVE
                feeling = "The user is highly engaged with relevant content"
        else:
            if sentiment == SentimentLevel.NEUTRAL:
                sentiment = SentimentLevel.NEGATIVE
                feeling = "The content doesn't seem to match the user's interests"
                
        return sentiment, feeling
        
    def detect_bug(
        self, 
        action_result: str, 
        page_state: Dict[str, any]
    ) -> Tuple[bool, Optional[BugType], Optional[str]]:
        """Detect if a bug occurred based on action result and page state."""
        if not action_result:
            return False, None, None
            
        result_lower = action_result.lower()
        
        for pattern, bug_type in self.error_patterns.items():
            if pattern in result_lower:
                description = self._generate_bug_description(bug_type, action_result)
                return True, bug_type, description
                
        if "error" in result_lower:
            return True, BugType.UNKNOWN, action_result
            
        return False, None, None
        
    def check_dropoff_condition(
        self,
        interactions: List[Interaction],
        persona_bio: str,
        ux_question: str
    ) -> Tuple[bool, Optional[str]]:
        """Check if user would likely drop off based on persona and interactions."""
        if len(interactions) < 3:
            return False, None
            
        recent_sentiment = [i.sentiment for i in interactions[-3:]]
        negative_count = sum(1 for s in recent_sentiment if s in [SentimentLevel.NEGATIVE, SentimentLevel.FRUSTRATED])
        
        if negative_count >= 2:
            if not self._check_persona_interest(interactions, persona_bio):
                return True, "User lost interest due to irrelevant content"
            else:
                return True, "User frustrated by poor UX despite interest in content"
                
        if len(interactions) > 10:
            if not any(self._is_meaningful_progress(i) for i in interactions[-5:]):
                return True, "User gave up after lack of meaningful progress"
                
        return False, None
        
    def generate_dynamic_thought(
        self,
        sentiment: SentimentLevel,
        bug_detected: bool,
        action_type: ActionType,
        page_context: str
    ) -> str:
        """Generate dynamic thoughts based on current state."""
        if bug_detected:
            if sentiment == SentimentLevel.FRUSTRATED:
                return "This is really frustrating. The site keeps having issues."
            else:
                return "Hmm, encountered an issue. Let me try a different approach."
                
        if sentiment == SentimentLevel.VERY_POSITIVE:
            return f"Great! This is exactly what I was looking for."
        elif sentiment == SentimentLevel.POSITIVE:
            return f"This looks good. Let me {action_type.value} here."
        elif sentiment == SentimentLevel.NEGATIVE:
            return f"This isn't quite what I expected. Let me see if I can find what I need."
        elif sentiment == SentimentLevel.FRUSTRATED:
            return f"This is taking too long. The site seems confusing."
        else:
            return f"Let me {action_type.value} to explore further."
            
    def _detect_repeated_actions(self, interactions: List[Interaction]) -> int:
        """Count repeated similar actions."""
        if len(interactions) < 2:
            return 0
            
        repeated = 0
        for i in range(1, len(interactions)):
            if (interactions[i].action_type == interactions[i-1].action_type and
                interactions[i].selector == interactions[i-1].selector):
                repeated += 1
                
        return repeated
        
    def _calculate_time_spent(self, interactions: List[Interaction]) -> timedelta:
        """Calculate time spent on recent interactions."""
        if len(interactions) < 2:
            return timedelta(0)
            
        return interactions[-1].ts - interactions[0].ts
        
    def _check_persona_interest(self, interactions: List[Interaction], persona_bio: str) -> bool:
        """Check if content aligns with persona interests."""
        persona_keywords = persona_bio.lower().split()
        content_keywords = []
        
        for interaction in interactions:
            if interaction.thought:
                content_keywords.extend(interaction.thought.lower().split())
                
        matching_keywords = sum(1 for keyword in persona_keywords if keyword in content_keywords)
        return matching_keywords >= 2
        
    def _is_meaningful_progress(self, interaction: Interaction) -> bool:
        """Check if an interaction represents meaningful progress."""
        meaningful_actions = [ActionType.CLICK, ActionType.FILL, ActionType.NAV]
        
        # Define successful action results
        successful_results = [
            "clicked", "filled", "navigated", "scrolled",
            "clicked_with_fallback", "filled_with_", "scrolled_to_element"
        ]
        
        # Check if action was successful
        is_successful = any(success_term in interaction.result.lower() 
                          for success_term in successful_results)
        
        return (interaction.action_type in meaningful_actions and 
                not interaction.bug_detected and
                is_successful)
                
    def _generate_bug_description(self, bug_type: BugType, result: str) -> str:
        """Generate a descriptive bug report."""
        descriptions = {
            BugType.UI_ERROR: f"UI element issue: {result}",
            BugType.LOADING_ERROR: f"Page loading problem: {result}",
            BugType.INTERACTION_FAILURE: f"Could not interact with element: {result}",
            BugType.VALIDATION_ERROR: f"Validation failed: {result}",
            BugType.NAVIGATION_ERROR: f"Navigation error: {result}",
            BugType.UNKNOWN: f"Unknown error: {result}"
        }
        return descriptions.get(bug_type, result)