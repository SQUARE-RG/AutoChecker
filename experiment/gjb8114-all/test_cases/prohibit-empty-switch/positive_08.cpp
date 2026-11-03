int add_bias(unsigned int value) {
    switch (value) {
        case 0U: {
            int bias = 10;
            return bias + static_cast<int>(value);
        }
    }
    return static_cast<int>(value);
}

int main() {
    return add_bias(0U) == 10 ? 0 : 1;
}
