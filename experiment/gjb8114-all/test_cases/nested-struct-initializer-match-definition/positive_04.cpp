struct Point {
    int x;
    int y;
};

struct Segment {
    Point start;
    Point end;
};

int main() {
    Segment segments[2] = {
        {{1, 2}, {3, 4}},
        {{5, 6}, {7, 8}}
    };
    return 0;
}
