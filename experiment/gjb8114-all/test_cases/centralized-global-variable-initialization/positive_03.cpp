inline int g_threshold;

namespace AppInit {
    void InitializeGlobals() {
        g_threshold = 50;
    }
}

int main() {
    AppInit::InitializeGlobals();
    return g_threshold == 50 ? 0 : 1;
}
