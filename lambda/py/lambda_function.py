# -*- coding: utf-8 -*-
import random
import logging
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler, AbstractExceptionHandler
from ask_sdk_core.utils import is_request_type, is_intent_name
from ask_sdk_model.ui import SimpleCard

sb = SkillBuilder()
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

WELCOME = "Welcome to Cassie Crossing! You are Cassie the chicken. Cross the road! Say start game."
HELP = "Say start game, then go forward, left, or right. 3 lives, 5 lanes."
START = "Game started! 5 lanes ahead. Say go forward! Watch for cars!"

class LaunchHandler(AbstractRequestHandler):
    def can_handle(self, h):
        return is_request_type("LaunchRequest")(h)
    def handle(self, h):
        h.attributes_manager.session_attributes = {"lane":0,"lives":3,"corn":0}
        return h.response_builder.speak(WELCOME+" "+START).ask(HELP).set_card(SimpleCard("Cassie Crossing",WELCOME)).response

class StartHandler(AbstractRequestHandler):
    def can_handle(self, h):
        return is_intent_name("StartGameIntent")(h) or is_intent_name("AMAZON.YesIntent")(h)
    def handle(self, h):
        h.attributes_manager.session_attributes = {"lane":0,"lives":3,"corn":0}
        return h.response_builder.speak(START).ask("Say go forward").response

class MoveHandler(AbstractRequestHandler):
    def can_handle(self, h):
        return is_intent_name("MoveIntent")(h) or is_intent_name("AMAZON.NextIntent")(h)
    def handle(self, h):
        s = h.attributes_manager.session_attributes
        lane = s.get("lane",0)
        lives = s.get("lives",3)
        corn = s.get("corn",0)
        try:
            direction = h.request_envelope.request.intent.slots["direction"].value.lower()
        except:
            direction = "forward"
        event = random.choice(["safe","car","car","corn","safe","safe"])
        say = ""
        if "forward" in direction or "ahead" in direction:
            lane += 1
            if event == "car":
                lives -= 1
                say = f"Car! You lost a life. {lives} left. "
                if lives <= 0:
                    return h.response_builder.speak(f"Game over at lane {lane}. You got {corn} corn. Say start game again.").response
            elif event == "corn":
                corn += 1
                say = f"Cluck! Corn found! {corn} total. Lane {lane}. "
            else:
                say = f"Safe! Lane {lane}. "
            if lane >= 5:
                return h.response_builder.speak(f"You won! Cassie crossed! {corn} corn, {lives} lives left! Say start game to play again.").response
        else:
            say = f"Dodged {direction}! Smart chicken! "
            if event == "corn":
                corn += 1
                say += f"Corn! Total {corn}. "
        s["lane"]=lane
        s["lives"]=lives
        s["corn"]=corn
        say += f"Lane {lane} of 5. Lives {lives}. Go forward, left, or right?"
        return h.response_builder.speak(say).ask("Forward left or right?").response

class HelpHandler(AbstractRequestHandler):
    def can_handle(self, h):
        return is_intent_name("AMAZON.HelpIntent")(h)
    def handle(self, h):
        return h.response_builder.speak(HELP).ask(HELP).response

class StopHandler(AbstractRequestHandler):
    def can_handle(self, h):
        return is_intent_name("AMAZON.StopIntent")(h) or is_intent_name("AMAZON.CancelIntent")(h)
    def handle(self, h):
        return h.response_builder.speak("Thanks for playing Cassie Crossing! Goodbye!").set_should_end_session(True).response

class FallbackHandler(AbstractRequestHandler):
    def can_handle(self, h):
        return is_intent_name("AMAZON.FallbackIntent")(h)
    def handle(self, h):
        return h.response_builder.speak("Say go forward, left, or right.").ask("Go forward?").response

class SessionHandler(AbstractRequestHandler):
    def can_handle(self, h):
        return is_request_type("SessionEndedRequest")(h)
    def handle(self, h):
        return h.response_builder.response

class ErrorHandler(AbstractExceptionHandler):
    def can_handle(self, h, e):
        return True
    def handle(self, h, e):
        logger.error(e, exc_info=True)
        return h.response_builder.speak("Error, try again.").ask("Try again?").response

sb.add_request_handler(LaunchHandler())
sb.add_request_handler(StartHandler())
sb.add_request_handler(MoveHandler())
sb.add_request_handler(HelpHandler())
sb.add_request_handler(StopHandler())
sb.add_request_handler(FallbackHandler())
sb.add_request_handler(SessionHandler())
sb.add_exception_handler(ErrorHandler())

lambda_handler = sb.lambda_handler()
