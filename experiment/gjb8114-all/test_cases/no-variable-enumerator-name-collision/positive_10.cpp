enum Color { red, green, blue };

int main() {
    auto value = [shade = 1]() {
        return shade + red;
    };
    return value();
}
