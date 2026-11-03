namespace app {
namespace globals {
int* g_buffer;
}

namespace init {
void InitializeGlobals() {
    globals::g_buffer = new int[16];
}
}
}

int main() {
    app::init::InitializeGlobals();
    delete[] app::globals::g_buffer;
    return 0;
}
