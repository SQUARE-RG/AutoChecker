#include <iostream>

struct Shape {
    virtual int area(int scale) const = 0;
    virtual ~Shape() = default;
};

struct Tagged {
    int tag = 0;
};

class Circle final : public Shape, public Tagged {
public:
    int area(int scale) const; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-2]
};

int Circle::area(int scale) const {
    return 3 * scale;
}

int main() {
    Circle c;
    Shape& shape = c;
    int result = shape.area(2);
    (void)result;
    return 0;
}
