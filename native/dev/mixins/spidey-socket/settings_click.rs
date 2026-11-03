// A click on the mod's settings page.
fn plug_settings_click(game: &crate::game::Game<'_>, mod_id: &str, button: usize) {
    crate::game::spidey_socket::settings_click(game, mod_id, button)
}
