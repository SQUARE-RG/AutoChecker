#include <array>

std::array<double, 3> g_weights;

namespace AppInit {
void InitializeGlobals() {
    g_weights[0] = 0.25;
    g_weights[1] = 0.35;
    g_weights[2] = 0.40;
}
}

int main() {
    AppInit::InitializeGlobals();
    return static_cast<int>(g_weights[0] * 100.0);
}
