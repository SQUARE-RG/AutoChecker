struct Scale {
    int apply(int value, int factor = 2) const {
        return value * factor;
    }
};

int main() {
    Scale s;
    return s.apply(5);
}
