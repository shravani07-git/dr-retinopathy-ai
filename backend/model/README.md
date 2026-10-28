# Model folder

Place your trained model here as:

`dr_efficientnet_b0.pt`

The backend expects a torchvision EfficientNet-B0 whose final classifier has 5 outputs:

0. No DR
1. Mild DR
2. Moderate DR
3. Severe DR
4. Proliferative DR

If the file is absent, the application clearly switches to **Demo Model** mode. The demo output is not medically meaningful.
