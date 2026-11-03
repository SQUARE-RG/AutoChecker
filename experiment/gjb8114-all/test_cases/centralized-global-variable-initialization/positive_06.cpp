#include <string>
#include <utility>

namespace app {
namespace globals {
std::pair<int, std::string> g_config;
}

namespace init {
void InitializeGlobals() {
    globals::g_config = std::make_pair(7, std::string("ready"));
}
}
}

int main() {
    app::init::InitializeGlobals();
    return app::globals::g_config.first;
}
