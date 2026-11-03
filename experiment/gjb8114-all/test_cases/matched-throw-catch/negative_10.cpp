class Base {
public:
    virtual ~Base() = default;
};

class Derived : public Base {};
class Other {};

int main() {
    try {
        throw new Derived(); // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-8-2]
    } catch (Other*) {
    }
    return 0;
}
