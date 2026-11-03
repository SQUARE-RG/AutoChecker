#include <cstdint>

// Shared with other translation units and updated by an external plugin thread.
inline int g_plugin_state = 0; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-1-13-12]

void plugin_set_state(int state) {
    g_plugin_state = state;
}

int plugin_get_state() {
    return g_plugin_state;
}
