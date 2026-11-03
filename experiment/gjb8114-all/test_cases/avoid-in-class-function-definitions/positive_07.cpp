namespace geometry {
class Shape {
public:
    virtual auto scaled_area(int factor) const noexcept -> int;
};
auto Shape::scaled_area(int factor) const noexcept -> int {
    return factor * 10;
}
}
int main() {
    geometry::Shape shape;
    return shape.scaled_area(2);
}
