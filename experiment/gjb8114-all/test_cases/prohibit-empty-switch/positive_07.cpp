bool is_true(bool flag) {
    switch (flag) {
        case true:
            return true;
        case false:
            return false;
    }
    return false;
}

int main() {
    return is_true(true) ? 0 : 1;
}
