#include <cstdint>

// Shared with other translation units and updated by an external plugin thread.
inline volatile int g_plugin_state = 0;

void plugin_set_state(int state) {
    g_plugin_state = state;
}

int plugin_get_state() {
    return g_plugin_state;
}
