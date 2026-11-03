#include <iostream>
class AbstractShape { // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-2-2]
public:
    virtual ~AbstractShape() {}
    virtual double area() const = 0;
};
int main() {
    return 0;
}
