// positive_10.cpp
#include <utility>

int main() {
    auto [frontSpeed, backSpeed] = std::make_pair(1, 2);
    return frontSpeed + backSpeed;
}
