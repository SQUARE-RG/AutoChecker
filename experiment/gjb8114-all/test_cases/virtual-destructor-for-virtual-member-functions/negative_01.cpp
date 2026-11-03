#include <iostream>

class Shape {
public:
    Shape() = default;
    ~Shape() {}  // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-r-2-3-1]
    virtual double area() const = 0;
    virtual const char* name() const = 0;
};

class Square : public Shape {
public:
    explicit Square(double sideLength) : side(sideLength) {}
    double area() const override { return side * side; }
    const char* name() const override { return "Square"; }
private:
    double side;
};

int main()
{
    Shape* shape = new Square(4.0);
    std::cout << shape->name() << " " << shape->area() << std::endl;
    delete shape;
    return 0;
}
