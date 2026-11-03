struct SpeedInfo {
    int speed0;
    int speed1;
};

int main() {
    SpeedInfo info{0, 1};
    return info.speed0 + info.speed1;
}
