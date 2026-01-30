import { TrendingUp } from "lucide-react"
import { Bar, BarChart, CartesianGrid, LabelList, XAxis } from "recharts"

import {
  Card,
  CardContent,
  CardDescription,
  CardFooter,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartContainer,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"

export const description = "A bar chart with a label"

const chartData = [
  { month: "Mon", attacks: 186 },
  { month: "Tue", attacks: 305 },
  { month: "Wed", attacks: 237 },
  { month: "Thu", attacks: 73 },
  { month: "Fri", attacks: 209 },
  { month: "Sat", attacks: 214 },
]

const chartConfig = {
  attacks: {
    label: "Attacks",
    color: "var(--chart-1)",
  },
} satisfies ChartConfig

function ChartBarLabel() {
  return (
    <Card className="bg-[#16161a] border border-[#232329] rounded-2xl p-4 sm:p-6 flex flex-col  justify-between hover:border-fuchsia-500/50 transition-all cursor-default">
      <div>
        <CardTitle className="text-xl font-bold">Attacks Timeline</CardTitle>
        <CardDescription className="text-xs font-medium text-gray-400">This week</CardDescription>
      </div>
      <div>
        <ChartContainer config={chartConfig}>
          <BarChart
            accessibilityLayer
            data={chartData}
            margin={{
              top: 20,
            }}
          >
            <CartesianGrid vertical={false} />
            <XAxis
              dataKey="month"
              tickLine={false}
              tickMargin={10}
              axisLine={false}
              tickFormatter={(value) => value.slice(0, 3)}
            />
            <ChartTooltip
              cursor={false}
              content={<ChartTooltipContent hideLabel />}
            />
            <Bar dataKey="attacks" fill="var(--color-attacks)" radius={8}>
              <LabelList
                position="top"
                offset={12}
                className="text-sm font-medium fill-foreground"
                fontSize={12}
              />
            </Bar>
          </BarChart>
        </ChartContainer>
      </div>
      {/* <CardFooter className="flex-col items-start gap-2 text-sm">
        <div className="flex gap-2 leading-none font-medium">
          Trending up by 5.2% this month <TrendingUp className="h-4 w-4" />
        </div>
        <div className="text-muted-foreground leading-none">
          Showing total visitors for the last 6 months
        </div>
      </CardFooter> */}
    </Card>
  )
}
export default ChartBarLabel