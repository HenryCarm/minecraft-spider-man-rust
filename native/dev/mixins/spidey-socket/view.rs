// The wall camera's turn of the whole view, put into the game's view pose.
fn turned_view(value: glam::Mat4) -> glam::Mat4 {
    value * crate::game::spidey_socket::view_fix()
}
