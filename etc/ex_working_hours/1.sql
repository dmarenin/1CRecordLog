USE [ex_working_hours]
GO

/****** Object:  Table [dbo].[work_hours]    Script Date: 11.11.2018 13:27:56 ******/
SET ANSI_NULLS ON
GO

SET QUOTED_IDENTIFIER ON
GO

CREATE TABLE [dbo].[work_hours](
	[empl] [nchar](32) NULL,
	[doc] [nchar](32) NULL,
	[dt_upd] [datetime] NULL,
	[num_str] [int] NULL,
	[period] [datetime] NULL,
	[period_offset] [int] NULL,
	[period_value] [smallint] NULL,
	[dep] [nchar](32) NULL
) ON [PRIMARY]

GO


