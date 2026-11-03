#include <iostream>

struct Coordinate {
    int x;
    int y;
};

int gOffset = 5;

class Trace {
public:
    explicit Trace(int steps);
    int getSteps() const;
private:
    int steps;
};

Trace::Trace(int s) : steps(s) {
    Coordinate start{0, 0};
    Coordinate end{steps, steps};
    (void)start;
    (void)end;
}

int Trace::getSteps() const {
    return steps;
}

int main() {
    Trace t(4);
    std::cout << t.getSteps() + gOffset << '\n';
    return 0;
}
