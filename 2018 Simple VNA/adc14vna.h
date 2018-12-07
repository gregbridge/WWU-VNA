/*
 * adc14.h
 *
 *  Created on: May 2, 2017
 *      Author: frohro
 */

#ifndef ADC14VNA_H_
#define ADC14VNA_H_
#include <ti/sysbios/family/arm/m3/Hwi.h>
#include <ti/devices/msp432p4xx/driverlib/driverlib.h>
#include "driverlib/dma.h"
#include "driverlib/adc14.h"

#define SMCLK_FREQUENCY     12000000

int adc14_main(void);
void startConversion(void);
void ADC14_IRQHandler(void);
void DMA_INT1_IRQHandler(void);
void DMA_INT2_IRQHandler(void);

#endif /* ADC14VNA_H_ */
