template <typename T, typename U>
T first(T value, U) {
    return value;
}

int main() {
    return first(7, 3.5);
}
