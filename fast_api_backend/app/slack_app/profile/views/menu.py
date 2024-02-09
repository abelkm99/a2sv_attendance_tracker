# from slack_sdk.models.blocks import (
#     PlainTextObject,
#     SectionBlock,
#     HeaderBlock,
#     MarkdownTextObject,
#     ButtonElement,
#     DividerBlock,
# )
# from slack_sdk.models.views import View

# unique_identifier = "profile_menu_"

# header = HeaderBlock(
#     text=PlainTextObject(text="Profile", emoji=True),
# )

# add_project_section = SectionBlock(
#     text=MarkdownTextObject(text="Register a User"),
#     accessory=ButtonElement(
#         text=PlainTextObject(text="Register", emoji=True),
#         action_id=f"{unique_identifier}register_user",
#         style="primary",
#     ),
# )
# update_project_section = SectionBlock(
#     text=MarkdownTextObject(text="Edit the profile"),
#     accessory=ButtonElement(
#         text=PlainTextObject(text="Update Profile", emoji=True),
#         action_id=f"{unique_identifier}update_profile",
#         style="primary",
#     ),
# )
# delete_project_section = SectionBlock(
#     text=MarkdownTextObject(text="View User"),
#     accessory=ButtonElement(
#         text=PlainTextObject(text="View Profile", emoji=True),
#         action_id=f"{unique_identifier}View_User",
#         # style="prima"
#     ),
# )

# divider = DividerBlock()


# def get_profile_menu():
#     return View(
#         type="modal",
#         callback_id=f"{unique_identifier}view_callback",
#         title=PlainTextObject(text="Attendance Monitoring", emoji=True),
#         close=PlainTextObject(text="Cancel", emoji=True),
#         blocks=[
#             header,
#             divider,
#             add_project_section,
#             divider,
#             update_project_section,
#             divider,
#             delete_project_section,
#         ],
#     )
