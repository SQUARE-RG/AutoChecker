#include <stdexcept>

class Resource {
public:
    Resource() : values{1, 2, 3} {}
    ~Resource() noexcept(false);
private:
    int values[3];
};

Resource::~Resource() noexcept(false) {
    try {
        for (int i = 0; i < 3; ++i) {
            if (values[i] == 2) {
                throw std::out_of_range("bad value");
            }
        }
    } catch (const std::out_of_range&) {
    }
}

int main() {
    Resource r;
    return 0;
}
