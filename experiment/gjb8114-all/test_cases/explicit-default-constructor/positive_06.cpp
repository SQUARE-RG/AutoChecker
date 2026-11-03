#include <iostream>
class AbstractShape {
public:
    AbstractShape() {}
    virtual ~AbstractShape() {}
    virtual double area() const = 0;
};
int main() {
    return 0;
}
