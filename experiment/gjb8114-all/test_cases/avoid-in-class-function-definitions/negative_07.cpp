namespace geometry {
class Shape {
public:
    virtual auto scaled_area(int factor) const noexcept -> int // CHECK-MESSAGES: :[[@LINE]]:{{[0-9]+}}: warning: {{.*}} [ucassaat-a-2-7-1]
    {
        return factor * 10;
    }
};
}
int main() {
    geometry::Shape shape;
    return shape.scaled_area(2);
}
