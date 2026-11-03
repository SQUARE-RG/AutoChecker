// positive_09.cpp
int main() {
    auto compute = [](int frontSpeed, int backSpeed) {
        return frontSpeed + backSpeed;
    };
    return compute(1, 2);
}
