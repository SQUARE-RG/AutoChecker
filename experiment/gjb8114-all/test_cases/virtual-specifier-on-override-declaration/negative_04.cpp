#include <iostream>

class Shape {
public:
    virtual ~Shape() = default;
    virtual double area() const;
};

double Shape::area() const {
    return 0.0;
}

class Circle : virtual public Shape {
public:
    double area() const; // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-4-2]
};

double Circle::area() const {
    return 3.14;
}

int main() {
    Circle c;
    Shape& s = c;
    double a = s.area();
    double b = c.area();
    return (a == b) ? 0 : 1;
}
