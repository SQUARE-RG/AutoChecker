void nested_switches(int v) {
    switch (v) {
        case 1:
            switch (v) {
                case 1:
                    switch (v) {
                        case 1:
                            switch (v) {
                                case 1:
                                    switch (v) {
                                        case 1:
                                            switch (v) {
                                                case 1:
                                                    switch (v) {
                                                        case 1:
                                                            break;
                                                        default:
                                                            break;
                                                    }
                                                    break;
                                                default:
                                                    break;
                                            }
                                            break;
                                        default:
                                            break;
                                    }
                                    break;
                                default:
                                    break;
                            }
                            break;
                        default:
                            break;
                    }
                    break;
                default:
                    break;
            }
            break;
        default:
            break;
    }
}
