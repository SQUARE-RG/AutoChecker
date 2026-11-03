struct RuntimeConfig {
    int max_workers;
    bool verbose;
};

RuntimeConfig g_config;

namespace AppInit {
    void InitializeGlobals() {
        g_config.max_workers = 8;
        g_config.verbose = false;
    }
}

int main() {
    AppInit::InitializeGlobals();
    return g_config.max_workers == 8 && !g_config.verbose ? 0 : 1;
}
