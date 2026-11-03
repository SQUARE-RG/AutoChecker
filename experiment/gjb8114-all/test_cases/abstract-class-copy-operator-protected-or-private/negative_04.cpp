#include <cstdint>

struct AbstractShape {
    virtual ~AbstractShape() = default;
    virtual int sides() const = 0;

    AbstractShape& operator=(AbstractShape const& rhs) { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-1-4]
        value_ = rhs.value_;
        return *this;
    }

private:
    int value_ = 0;
};

class ShapeImpl final : public AbstractShape {
public:
    int sides() const override { return 3; }
};

int main() {
    ShapeImpl shape;
    return shape.sides();
}
