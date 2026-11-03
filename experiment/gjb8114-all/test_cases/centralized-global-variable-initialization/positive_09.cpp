#include <optional>
#include <string>

std::optional<std::string> g_service_name;

namespace AppInit {
void InitializeGlobals() {
    g_service_name = "billing";
}
}

int main() {
    AppInit::InitializeGlobals();
    return g_service_name ? 0 : 1;
}
