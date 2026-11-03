#include <cstdio>
#include <stdexcept>

int main()
{
    try {
        auto bail_out = []() {
            std::puts("bailing out");
            throw std::runtime_error("bail out");
        };

        bail_out();
    } catch (const std::runtime_error& e) {
        std::printf("recovered: %s\n", e.what());
        return 0;
    }

    return 0;
}
