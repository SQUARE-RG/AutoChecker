#include <iostream>

enum class Shade { Light, Dark };

class ShadeWrapper {
public:
    ShadeWrapper(Shade shade) : shade_(shade) {} // CHECK-MESSAGES: :[[@LINE]]:5: warning: {{.*}} [ucassaat-r-2-2-3]
    Shade shade() const { return shade_; }
private:
    Shade shade_;
};

int main() {
    ShadeWrapper wrapper = {Shade::Dark};
    std::cout << static_cast<int>(wrapper.shade()) << '\n';
    return 0;
}
