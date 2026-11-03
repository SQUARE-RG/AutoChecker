#include <vector>

namespace app {

std::vector<int> g_config_values;

namespace init {

void InitializeGlobals() {
    g_config_values = {10, 20, 30};
}

} // namespace init

} // namespace app

int main() {
    app::init::InitializeGlobals();
    return app::g_config_values.size() == 3 ? 0 : 1;
}
