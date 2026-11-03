struct Geometry {
    Geometry() : width(0), height(0) {}
    int width;
    int height;
};

int main() {
    Geometry g;
    return g.width + g.height;
}
