## Guild Data
guild_id : str
active : bool
guild_prefix : str

## Welcome Messages
guild_id : str
active : bool
channel_id : str
text_color : str
background_image_url : str

## Level Up
guild_id : str
active : bool
user_data : dict => { member_id : xp }

## Custom Commands
guild_id : str
active : bool
command_name_to_message_map : dict => { command_name : message }

## Timed Messages
guild_id : str
active : bool
alias_to_timed_message_map : dict => {
    alias : [
        channel_id, 
        period, 
        message
    ]}

## Reaction Roles
guild_id : str
active : bool
message_role_reaction_map : dict => { 
    message_id : [
        channel_id, 
        message_content, 
        embed : [
            title, 
            description
        ], 
        { role_id : reaction_id }
    ]}

## Ticket System
guild_id : str
active : bool
message_to_ticket_map : dict => { 
    message_id : [
        title,
        desc,
        channel_id,
        category_id,
        {
            message_id : [
                ticket_id,
            ]
        }
    ]
}

## Stat Channel
guild_id : str
active : bool
stat_channel_id : str