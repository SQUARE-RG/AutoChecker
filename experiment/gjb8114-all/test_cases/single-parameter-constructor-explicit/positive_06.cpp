#include <iostream>

enum class Shade { Light, Dark };

class ShadeWrapper {
public:
    explicit ShadeWrapper(Shade shade) : shade_(shade) {}
    Shade shade() const { return shade_; }
private:
    Shade shade_;
};

int main() {
    ShadeWrapper wrapper{Shade::Dark};
    std::cout << static_cast<int>(wrapper.shade()) << '\n';
    return 0;
}
