enum class Color { Red, Green, Blue };

int classify(Color c) {
    int result = 0;
    switch (c)
    {
        case Color::Red:
            result = 1;
            break;
        case Color::Green:
            result = 2;
            break;
        case Color::Blue:
            result = 3;
            break;
    }
    return result;
}

int main() {
    return classify(Color::Green);
}
